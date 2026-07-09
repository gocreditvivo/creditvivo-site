const crypto = require("crypto");
const { security } = require("./config");

const postAttempts = new Map();

function clientKey(req) {
  return crypto
    .createHash("sha256")
    .update(`${req.socket.remoteAddress || "unknown"}:${req.headers["user-agent"] || ""}`)
    .digest("hex")
    .slice(0, 24);
}

function isRateLimited(req) {
  const key = clientKey(req);
  const now = Date.now();
  const existing = postAttempts.get(key) || [];
  const recent = existing.filter((timestamp) => now - timestamp < security.postLimitWindowMs);
  recent.push(now);
  postAttempts.set(key, recent);
  return recent.length > security.postLimitMax;
}

function isAdmin(req) {
  const header = String(req.headers["x-admin-token"] || "");
  const token = security.adminToken;
  if (!header || header.length !== token.length) return false;
  return crypto.timingSafeEqual(Buffer.from(header), Buffer.from(token));
}

function timingMatch(input, expected) {
  const value = String(input || "");
  const target = String(expected || "");
  if (!value || value.length !== target.length) return false;
  return crypto.timingSafeEqual(Buffer.from(value), Buffer.from(target));
}

function isFounderDevice(req) {
  const deviceKey = String(req.headers["x-founder-device-key"] || "");
  const phoneHash = String(req.headers["x-founder-phone-sha256"] || "");
  const phoneLast4 = String(req.headers["x-founder-phone-last4"] || "");
  const phoneMatches = security.founderPhoneSha256
    ? timingMatch(phoneHash, security.founderPhoneSha256)
    : timingMatch(phoneLast4, security.founderPhoneLast4);

  return timingMatch(deviceKey, security.founderDeviceKey) && phoneMatches;
}

function hashIp(req) {
  return crypto
    .createHash("sha256")
    .update(String(req.socket.remoteAddress || "unknown"))
    .digest("hex")
    .slice(0, 16);
}

module.exports = { isAdmin, isFounderDevice, isRateLimited, hashIp };
