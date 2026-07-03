import { existsSync, mkdirSync } from "node:fs";
import { join, resolve } from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const root = resolve(fileURLToPath(new URL("..", import.meta.url)));
const backend = join(root, "scanner_backend");
const python = existsSync(join(backend, ".venv", "Scripts", "python.exe"))
  ? join(backend, ".venv", "Scripts", "python.exe")
  : "python";
const tmp = join(backend, ".tmp", "npm-build-pytest");
mkdirSync(tmp, { recursive: true });

function run(args, options = {}) {
  const result = spawnSync(args[0], args.slice(1), {
    cwd: options.cwd ?? backend,
    stdio: "inherit",
    shell: false,
    env: {
      ...process.env,
      TMP: join(backend, ".tmp"),
      TEMP: join(backend, ".tmp"),
    },
  });
  if (result.status !== 0) {
    process.exit(result.status ?? 1);
  }
}

run([python, "-m", "compileall", "-q", "-x", "[/\\\\](\\.venv|\\.tmp|__pycache__)[/\\\\]", "scanner_backend"], { cwd: root });
run([python, "-m", "pytest", "-q", "--basetemp", tmp], { cwd: backend });
