const path = require("path");
const fs = require("fs");

const ROOT = path.join(__dirname, "..");

function loadEnvFile() {
  if (process.env.NODE_ENV === "test" || process.env.CREDIT_VIVO_TEST_MODE === "true") return;
  const envPath = process.env.CREDIT_VIVO_ENV_FILE
    || path.join(process.env.USERPROFILE || ROOT, ".creditvivo", "minitim.env");
  if (!fs.existsSync(envPath)) return;
  const lines = fs.readFileSync(envPath, "utf8").split(/\r?\n/);
  lines.forEach((line) => {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#") || !trimmed.includes("=")) return;
    const [key, ...rest] = trimmed.split("=");
    if (!process.env[key]) {
      process.env[key] = rest.join("=").replace(/^["']|["']$/g, "");
    }
  });
}

loadEnvFile();

const ENV = process.env.NODE_ENV || "development";
const IS_PRODUCTION = ENV === "production";
const IS_TEST = ENV === "test" || process.env.CREDIT_VIVO_TEST_MODE === "true";
const PORT = Number(process.env.PORT || 8910);
const HOST = process.env.HOST || "127.0.0.1";
const ADMIN_TOKEN = process.env.ADMIN_TOKEN || "dev-admin-token-change-me";
const OPENAI_MODEL = process.env.OPENAI_MODEL || "gpt-5.5";
const FOUNDER_DEVICE_KEY = process.env.FOUNDER_DEVICE_KEY || "dev-founder-device-change-me";
const FOUNDER_PHONE_LAST4 = process.env.FOUNDER_PHONE_LAST4 || "0000";
const FOUNDER_PHONE_SHA256 = process.env.FOUNDER_PHONE_SHA256 || "";

if (IS_PRODUCTION && ADMIN_TOKEN === "dev-admin-token-change-me") {
  throw new Error("ADMIN_TOKEN must be set before running in production.");
}

if (IS_PRODUCTION && FOUNDER_DEVICE_KEY === "dev-founder-device-change-me") {
  throw new Error("FOUNDER_DEVICE_KEY must be set before running MiniTim in production.");
}

module.exports = {
  app: {
    name: "credit-vivo-platform",
    version: "0.2.0",
    env: ENV,
    isProduction: IS_PRODUCTION,
    isTest: IS_TEST,
    port: PORT,
    host: HOST,
    root: ROOT
  },
  security: {
    adminToken: ADMIN_TOKEN,
    founderDeviceKey: FOUNDER_DEVICE_KEY,
    founderPhoneLast4: FOUNDER_PHONE_LAST4,
    founderPhoneSha256: FOUNDER_PHONE_SHA256,
    postLimitWindowMs: 10 * 60 * 1000,
    postLimitMax: IS_TEST ? 100 : 8,
    maxBodyBytes: 20_000
  },
  storage: {
    dataDir: path.join(ROOT, "data"),
    leadsFile: path.join(ROOT, "data", IS_TEST ? "leads.test.json" : "leads.json"),
    workflowsFile: path.join(ROOT, "data", IS_TEST ? "workflows.test.json" : "workflows.json"),
    ceoMemoryFile: path.join(ROOT, "data", IS_TEST ? "ceo-memory.test.json" : "ceo-memory.json"),
    ceoActionsFile: path.join(ROOT, "data", IS_TEST ? "ceo-actions.test.json" : "ceo-actions.json"),
    ceoAuditFile: path.join(ROOT, "data", IS_TEST ? "ceo-audit.test.json" : "ceo-audit.json")
  },
  engine: {
    modelVersion: "cv-readiness-rules-v0.2.0",
    mode: process.env.CV_ENGINE_MODE || "rules-with-ai-ready-interface",
    allowSelfModify: false
  },
  ai: {
    provider: process.env.OPENAI_API_KEY ? "openai-responses" : "rules-fallback",
    openaiApiKey: process.env.OPENAI_API_KEY || "",
    openaiModel: OPENAI_MODEL,
    requestTimeoutMs: Number(process.env.OPENAI_TIMEOUT_MS || 20000)
  },
  twilio: {
    accountSid: process.env.TWILIO_ACCOUNT_SID || "",
    apiKey: process.env.TWILIO_API_KEY || "",
    apiSecret: process.env.TWILIO_API_SECRET || "",
    fromNumber: process.env.TWILIO_FROM_NUMBER || "",
    founderPhone: process.env.MINITIM_FOUNDER_PHONE || ""
  }
};
