import { sampleMarketAssets } from "../../lib/market/sampleAssets";
import CreativePreviewCard from "./CreativePreviewCard";

export default function MarketDashboard() {
  const assets = sampleMarketAssets;
  const stats = [
    ["Assets", assets.length],
    ["Needs Review", assets.filter((asset) => asset.status === "Needs Review").length],
    ["Learning Topics", 5],
    ["Approved", assets.filter((asset) => asset.status === "Approved").length],
  ];
  return (
    <main className="market-shell">
      <section className="market-hero">
        <p>Credit Vivo Market AI</p>
        <h1>In-house creative studio</h1>
        <p>Create learning videos, ad images, animations, captions, campaigns, and approved brand assets.</p>
      </section>
      <section className="market-stats">
        {stats.map(([label, value]) => <div key={label}><p>{label}</p><strong>{value}</strong></div>)}
      </section>
      <section className="market-grid">
        {assets.map((asset) => <CreativePreviewCard key={asset.asset_id} asset={asset} />)}
      </section>
    </main>
  );
}
