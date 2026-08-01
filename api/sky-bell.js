// Server-side proxy for the "sky-bell" Vercel Connect connector (api.perplexity.ai/sky-bell).
//
// This file MUST stay a Node.js function (not Python) because the Vercel Connect
// token SDK (`@vercel/connect`) is TypeScript/Node-only and reads the deployment's
// VERCEL_OIDC_TOKEN automatically at runtime. Vercel picks the runtime by file
// extension, so `.js` here runs on Node while `api/index.py` keeps running the
// FastAPI scanner backend on Python. See vercel.json for the rewrite that keeps
// this exact path from being swallowed by the Python catch-all route.
//
// Usage from the frontend or scanner backend:
//   POST /api/sky-bell
//   body: { "path": "/some/endpoint", "method": "GET" | "POST", "payload": { ... } }
//
// The connector access token is fetched fresh on every request (short-lived,
// auto-refreshed by the SDK) and is never returned to the caller — only the
// upstream response body/status is relayed back.

import { getToken } from '@vercel/connect';

const CONNECTOR_ID = 'api.perplexity.ai/sky-bell';
const SKY_BELL_BASE_URL = process.env.SKY_BELL_BASE_URL || 'https://api.perplexity.ai/sky-bell';

export default async function handler(req, res) {
  if (req.method !== 'POST' && req.method !== 'GET') {
    res.status(405).json({ error: 'method_not_allowed', message: 'Use GET or POST.' });
    return;
  }

  const body = typeof req.body === 'object' && req.body !== null ? req.body : {};
  const targetPath = typeof body.path === 'string' && body.path.length > 0 ? body.path : '/';
  const upstreamMethod = typeof body.method === 'string' ? body.method.toUpperCase() : 'GET';
  const payload = body.payload;

  let token;
  try {
    token = await getToken(CONNECTOR_ID, { subject: { type: 'app' } });
  } catch (error) {
    console.error('[sky-bell] failed to obtain connector token:', error);
    res.status(502).json({
      error: 'sky_bell_token_error',
      message: error instanceof Error ? error.message : 'Unable to obtain connector token.',
    });
    return;
  }

  const url = `${SKY_BELL_BASE_URL}${targetPath.startsWith('/') ? targetPath : `/${targetPath}`}`;

  try {
    const upstreamResponse = await fetch(url, {
      method: upstreamMethod,
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: ['GET', 'HEAD'].includes(upstreamMethod) || payload === undefined
        ? undefined
        : JSON.stringify(payload),
    });

    const contentType = upstreamResponse.headers.get('content-type') || 'application/json';
    const text = await upstreamResponse.text();

    res.status(upstreamResponse.status);
    res.setHeader('Content-Type', contentType);
    res.send(text);
  } catch (error) {
    console.error('[sky-bell] upstream request failed:', error);
    res.status(502).json({
      error: 'sky_bell_upstream_error',
      message: error instanceof Error ? error.message : 'Upstream request failed.',
    });
  }
}
