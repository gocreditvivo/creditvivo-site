// Thin client for the "sky-bell" connector, proxied through our own
// serverless function at /api/sky-bell (see api/sky-bell.js). The Vercel
// Connect access token is fetched and used server-side only — the browser
// never sees it.

export type SkyBellRequest = {
  path?: string;
  method?: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';
  payload?: unknown;
};

export async function callSkyBell<T = unknown>({
  path = '/',
  method = 'GET',
  payload,
}: SkyBellRequest): Promise<T> {
  const response = await fetch('/api/sky-bell', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ path, method, payload }),
  });

  const text = await response.text();
  const data = text ? JSON.parse(text) : null;

  if (!response.ok) {
    const message =
      (data && typeof data === 'object' && 'message' in data && (data as { message?: string }).message) ||
      `sky-bell request failed: ${response.status}`;
    throw new Error(message);
  }

  return data as T;
}
