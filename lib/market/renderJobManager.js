let renderJobs = [];

export function createRenderJob({ asset_id, template_id, format, duration_seconds }) {
  const job = {
    job_id: crypto.randomUUID(),
    asset_id,
    template_id,
    status: "Queued For Review",
    format,
    duration_seconds,
    output_path: null,
    created_at: new Date().toISOString(),
    completed_at: null,
    render_engine: "preview_placeholder",
    approval_required_before_export: true,
    auto_publish_allowed: false,
  };
  renderJobs.unshift(job);
  return job;
}

export function listRenderJobs() {
  return renderJobs;
}
