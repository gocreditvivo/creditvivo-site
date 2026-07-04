const baseUrl = process.env.UAT_BASE_URL || "http://127.0.0.1:3000";
const backendUrl = process.env.UAT_BACKEND_URL || "http://127.0.0.1:8082";

const frontendRoutes = [
  "/",
  "/signup",
  "/login",
  "/pricing",
  "/terms",
  "/privacy",
  "/disclosures",
  "/cancellation-refund",
  "/security",
  "/contact",
  "/checkout",
  "/checkout/success",
  "/member",
  "/member/upload",
  "/member/findings",
  "/member/accounts",
  "/member/disputes",
  "/member/progress",
  "/member/documents",
  "/member/messages",
  "/member/security",
];

async function requireText(url, patterns) {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`${url} returned ${response.status}`);
  }
  const text = await response.text();
  for (const pattern of patterns) {
    if (!text.includes(pattern)) {
      throw new Error(`${url} missing expected text: ${pattern}`);
    }
  }
  return true;
}

for (const route of frontendRoutes) {
  await requireText(`${baseUrl}${route}`, ["Credit Vivo"]);
}

await requireText(`${baseUrl}/member`, ["Production gate active"]);
await requireText(`${baseUrl}/signup`, ["staging safe mode"]);
await requireText(`${baseUrl}/checkout`, ["test"]);

const health = await fetch(`${backendUrl}/health`).then((response) => response.json());
if (!health.ok) {
  throw new Error("Backend health is not ok.");
}
if (health.email_sending_enabled !== false || health.dispute_email_auto_send_enabled !== false) {
  throw new Error("Email auto-send flags are not safely disabled.");
}

console.log("Credit Vivo staging UAT smoke passed.");
