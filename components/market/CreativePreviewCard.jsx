import AssetStatusBadge from "./AssetStatusBadge";

export default function CreativePreviewCard({ asset }) {
  return (
    <article className="creative-card">
      <div>
        <p>{asset.type} / {asset.format}</p>
        <h3>{asset.title}</h3>
      </div>
      <AssetStatusBadge status={asset.status} />
      <p>{asset.campaign}</p>
      <div>
        {(asset.tags || []).slice(0, 4).map((tag) => <span key={tag}>{tag}</span>)}
      </div>
      <strong>{asset.compliance_flags?.length ? "Compliance review needed" : "No blocked phrases found"}</strong>
    </article>
  );
}
