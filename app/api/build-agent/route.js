import { existsSync, readFileSync } from "node:fs";
import { spawnSync } from "node:child_process";
import { join } from "node:path";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const ROOT = process.cwd();
const MAX_INPUT_LENGTH = 8000;
const ALLOWED_ACTIONS = new Set(["snapshot", "analyze", "plan"]);

const sensitivePatterns = [
  [/\b\d{3}-?\d{2}-?\d{4}\b/g, "[REDACTED_SSN]"],
  [/\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13})\b/g, "[REDACTED_PAYMENT_CARD]"],
  [/\b(?:api[_-]?key|token|secret|password)\s*[:=]\s*[^\s,;]+/gi, "$1=[REDACTED]"],
  [/\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b/g, "[REDACTED_EMAIL]"],
];

function redact(value) {
  let output = String(value || "").slice(0, MAX_INPUT_LENGTH);
  for (const [pattern, replacement] of sensitivePatterns) {
    output = output.replace(pattern, replacement);
  }
  return output;
}

function runReadOnly(command, args) {
  const result = spawnSync(command, args, {
    cwd: ROOT,
    encoding: "utf8",
    shell: false,
    windowsHide: true,
    timeout: 8000,
  });

  return {
    ok: result.status === 0,
    exitCode: result.status,
    stdout: redact(result.stdout).trim(),
    stderr: redact(result.stderr).trim(),
  };
}

function parseGitStatus(raw) {
  const rows = String(raw || "").split(/\r?\n/).filter(Boolean);
  return {
    total: rows.length,
    modified: rows.filter((row) => row.startsWith(" M") || row.startsWith("M ")).length,
    deleted: rows.filter((row) => row.startsWith(" D") || row.startsWith("D ")).length,
    untracked: rows.filter((row) => row.startsWith("??")).length,
  };
}

function readPackage() {
  const path = join(ROOT, "package.json");
  if (!existsSync(path)) return null;
  try {
    const parsed = JSON.parse(readFileSync(path, "utf8"));
    return {
      name: parsed.name || "unknown",
      version: parsed.version || "unversioned",
      scripts: Object.keys(parsed.scripts || {}),
      dependencies: Object.keys(parsed.dependencies || {}),
      devDependencies: Object.keys(parsed.devDependencies || {}),
    };
  } catch {
    return null;
  }
}

function getSnapshot() {
  const branch = runReadOnly("git", ["status", "--short", "--branch"]);
  const porcelain = runReadOnly("git", ["status", "--porcelain"]);
  const head = runReadOnly("git", ["log", "-1", "--format=%h %s"]);
  const behind = runReadOnly("git", ["rev-list", "--count", "HEAD..origin/main"]);
  const ahead = runReadOnly("git", ["rev-list", "--count", "origin/main..HEAD"]);
  const status = parseGitStatus(porcelain.stdout);
  const paths = {
    nextApp: existsSync(join(ROOT, "app")),
    scannerBackend: existsSync(join(ROOT, "scanner_backend")),
    scannerClient: existsSync(join(ROOT, "src", "lib", "scannerApi.ts")),
    chatbot: existsSync(join(ROOT, "app", "api", "chatbot", "route.js")),
    buildAgent: existsSync(join(ROOT, "app", "api", "build-agent", "route.js")),
  };

  const blockers = [];
  if (!porcelain.ok) blockers.push("Git working-tree status could not be read.");
  if (status.total > 0) blockers.push(`${status.total} uncommitted working-tree changes require review.`);
  if (Number(behind.stdout || 0) > 0) blockers.push(`Local checkout is ${behind.stdout} commit(s) behind origin/main.`);
  if (!paths.scannerBackend) blockers.push("Scanner backend folder is not present in this working tree.");
  if (!readPackage()?.scripts.includes("build")) blockers.push("No build script is defined.");

  return {
    generatedAt: new Date().toISOString(),
    mode: "read_only_local_snapshot",
    branch: branch.stdout.split(/\r?\n/)[0] || "unavailable",
    head: head.stdout || "unavailable",
    divergence: {
      behindMain: Number(behind.stdout || 0),
      aheadOfMain: Number(ahead.stdout || 0),
    },
    workingTree: status,
    package: readPackage(),
    paths,
    blockers,
    permissions: {
      readsRepository: true,
      runsReadOnlyGit: true,
      editsFiles: false,
      deploys: false,
      sendsDisputes: false,
      acceptsCustomerReports: false,
    },
  };
}

const checks = [
  {
    id: "build",
    severity: "P1",
    patterns: [/failed to compile/i, /build failed/i, /module not found/i, /error TS\d+/i],
    title: "Production build is failing",
    next: "Resolve the first deterministic compiler error, then rerun the full production build.",
  },
  {
    id: "security",
    severity: "P1",
    patterns: [/high severity/i, /critical severity/i, /vulnerabilit/i, /CVE-\d+/i],
    title: "Dependency or security gate needs review",
    next: "Confirm the affected production dependency and test the smallest supported upgrade.",
  },
  {
    id: "scanner-auth",
    severity: "P0",
    patterns: [/unauthenticated/i, /missing.*token/i, /ownership/i, /cross[- ]customer/i, /customer isolation/i],
    title: "Scanner authorization or isolation risk",
    next: "Keep customer access blocked until authenticated ownership and cross-user isolation tests pass.",
  },
  {
    id: "privacy",
    severity: "P0",
    patterns: [/raw report/i, /full account/i, /social security/i, /\bssn\b/i, /unmasked/i],
    title: "Sensitive-data exposure risk",
    next: "Stop the affected output path, re-mask data, and test every generated artifact with synthetic fixtures.",
  },
  {
    id: "automation",
    severity: "P1",
    patterns: [/allow-scripts/i, /\bEPERM\b/i, /\bEBUSY\b/i, /permission denied/i],
    title: "Local automation is blocked",
    next: "Fix the local dependency or file-lock condition before treating deployment automation as healthy.",
  },
  {
    id: "success",
    severity: "INFO",
    patterns: [/tests? passed/i, /build completed/i, /compiled successfully/i],
    title: "A success signal appears in the supplied evidence",
    next: "Confirm the command exit code and verify the resulting artifact before recording a pass.",
  },
];

function analyzeEvidence(input) {
  const evidence = redact(input);
  const findings = checks
    .filter((check) => check.patterns.some((pattern) => pattern.test(evidence)))
    .map(({ id, severity, title, next }) => ({ id, severity, title, next }));

  if (!findings.length) {
    findings.push({
      id: "unknown",
      severity: "P2",
      title: "No known build or release signal was detected",
      next: "Provide the complete command, exit code, and error output before choosing a fix.",
    });
  }

  return {
    inputCharactersReviewed: evidence.length,
    redactionApplied: evidence !== String(input || "").slice(0, MAX_INPUT_LENGTH),
    verdict: findings.some((item) => item.severity === "P0")
      ? "BLOCKED"
      : findings.some((item) => item.severity === "P1")
        ? "NEEDS_REPAIR"
        : "REVIEW_REQUIRED",
    findings,
    approvalRequired: true,
    prohibitedActions: [
      "No production writes",
      "No real customer data",
      "No automatic merge or deployment",
      "No dispute, letter, complaint, or email sending",
    ],
  };
}

const plans = {
  build: {
    title: "Restore a passing application build",
    steps: [
      "Capture the current branch, commit, and dirty-tree inventory.",
      "Run the production build and preserve the first deterministic error.",
      "Make one scoped repair without deleting unrelated work.",
      "Rerun the build and relevant route checks.",
      "Present the diff and evidence for human approval.",
    ],
  },
  scanner: {
    title: "Verify scanner integration safely",
    steps: [
      "Use synthetic reports only and keep production writes disabled.",
      "Map upload, parse, result, and download contracts.",
      "Verify authentication, server-side ownership, masking, and output minimization.",
      "Run same-user and cross-user isolation tests.",
      "Require customer and admin approval before any draft leaves the system.",
    ],
  },
  compliance: {
    title: "Review customer-facing claims",
    steps: [
      "Locate the exact copy and user action.",
      "Flag guarantees, automatic actions, legal conclusions, and unclear fees.",
      "Rewrite as factual process language and possible review points.",
      "Keep human approval and attorney-review boundaries explicit.",
      "Record the reviewed surface and unresolved legal questions.",
    ],
  },
  release: {
    title: "Run the controlled release gate",
    steps: [
      "Require a clean, synchronized branch and passing production build.",
      "Require passing unit, integration, privacy, and cross-user isolation tests.",
      "Verify live routes, JavaScript, CSS, content types, and browser behavior.",
      "Confirm monitoring and rollback procedures.",
      "Release only after a named human approves the evidence package.",
    ],
  },
};

function getPlan(area) {
  const selected = plans[area] || plans.build;
  return {
    area: plans[area] ? area : "build",
    ...selected,
    approvalRequiredBeforeChanges: true,
    definitionOfDone: "Evidence is attached, the relevant gate passes, and a human approves the next state.",
  };
}

function isAgentEnabled(request) {
  if (process.env.NODE_ENV !== "production") return true;
  if (process.env.CREDITVIVO_BUILD_AGENT_ENABLED !== "true") return false;
  const expected = process.env.CREDITVIVO_BUILD_AGENT_KEY;
  if (!expected) return false;
  return request.headers.get("x-creditvivo-agent-key") === expected;
}

export async function GET(request) {
  if (!isAgentEnabled(request)) {
    return Response.json(
      { status: "disabled", message: "Build Agent is disabled outside the approved internal environment." },
      { status: 403 }
    );
  }

  return Response.json({ status: "ok", snapshot: getSnapshot() });
}

export async function POST(request) {
  if (!isAgentEnabled(request)) {
    return Response.json(
      { status: "disabled", message: "Build Agent is disabled outside the approved internal environment." },
      { status: 403 }
    );
  }

  const body = await request.json().catch(() => ({}));
  const action = String(body.action || "");
  if (!ALLOWED_ACTIONS.has(action)) {
    return Response.json({ status: "error", message: "Unsupported Build Agent action." }, { status: 400 });
  }

  if (action === "snapshot") {
    return Response.json({ status: "ok", snapshot: getSnapshot() });
  }
  if (action === "analyze") {
    return Response.json({ status: "ok", analysis: analyzeEvidence(body.input) });
  }

  return Response.json({ status: "ok", plan: getPlan(String(body.area || "build")) });
}
