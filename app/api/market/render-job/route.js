import { createRenderJob } from "../../../../lib/market/renderJobManager";

export async function POST(request) {
  return Response.json({ ok: true, render_job: createRenderJob(await request.json()) });
}
