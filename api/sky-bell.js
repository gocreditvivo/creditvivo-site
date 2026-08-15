// The unused privileged connector proxy is intentionally disabled for the RC.
// Reintroducing it requires a separately reviewed server-only implementation.
export default function handler(_req, res) {
  res.status(404).json({ error: 'not_found' });
}
