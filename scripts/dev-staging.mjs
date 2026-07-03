import { spawnSync } from "node:child_process";

const result = spawnSync("npm", ["run", "dev"], {
  shell: true,
  stdio: "inherit",
  env: {
    ...process.env,
    APP_ENV: "staging",
    NEXT_PUBLIC_APP_ENV: "staging",
    NEXT_PUBLIC_CREDIT_VIVO_DEMO_MODE: "false",
    NEXT_PUBLIC_CREDIT_VIVO_REQUIRE_PRODUCTION_GATES: "true",
    NEXT_PUBLIC_CREDIT_VIVO_REQUIRE_AUTH: "true",
    NEXT_PUBLIC_CREDIT_VIVO_API_BASE_URL: "http://127.0.0.1:8082",
    SCANNER_USE_SYNTHETIC_REPORTS: "true",
    SCANNER_ALLOW_REAL_CUSTOMER_DATA: "false",
    PAYMENTS_MODE: "test",
    STRIPE_MODE: "test",
    EMAIL_PROVIDER: "sandbox",
    ENABLE_EMAIL_SENDING: "false",
    ENABLE_MARKETING_EMAILS: "false",
    ENABLE_DISPUTE_EMAIL_AUTO_SEND: "false",
  },
});

process.exit(result.status ?? 1);

