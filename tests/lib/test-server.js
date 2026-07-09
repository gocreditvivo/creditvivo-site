const { spawn } = require("child_process");

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function waitForServer(baseUrl) {
  for (let attempt = 0; attempt < 40; attempt += 1) {
    try {
      const response = await fetch(`${baseUrl}/api/health`);
      const body = await response.json();
      if (response.ok && body.ok) return;
    } catch {
      await sleep(150);
    }
  }
  throw new Error(`Server did not start at ${baseUrl}`);
}

async function withTestServer(port, fn) {
  const baseUrl = `http://127.0.0.1:${port}`;
  const server = spawn(process.execPath, ["server.js"], {
    cwd: process.cwd(),
    env: {
      ...process.env,
      PORT: String(port),
      ADMIN_TOKEN: "benchmark-admin-token",
      NODE_ENV: "test"
    },
    stdio: "ignore",
    windowsHide: true
  });

  try {
    await waitForServer(baseUrl);
    return await fn({ baseUrl, adminToken: "benchmark-admin-token" });
  } finally {
    server.kill();
    await sleep(250);
  }
}

module.exports = { withTestServer };
