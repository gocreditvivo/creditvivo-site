export const assetStatuses = ["Draft", "Needs Review", "Compliance Review", "Approved", "Scheduled", "Published", "Archived", "Rejected"];

export function canPublish(asset) {
  return asset.status === "Approved" && (asset.compliance_flags || []).length === 0;
}

export function requireComplianceReview(asset) {
  return (asset.compliance_flags || []).length > 0 ? "Compliance Review" : "Needs Review";
}
