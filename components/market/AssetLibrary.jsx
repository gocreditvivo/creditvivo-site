import { sampleMarketAssets } from "../../lib/market/sampleAssets";
import CreativePreviewCard from "./CreativePreviewCard";

export default function AssetLibrary() {
  return <section className="market-grid">{sampleMarketAssets.map((asset) => <CreativePreviewCard key={asset.asset_id} asset={asset} />)}</section>;
}
