import { sampleMarketAssets } from "./sampleAssets";

let inMemoryAssets = [...sampleMarketAssets];

export function listMarketAssets() {
  return inMemoryAssets;
}

export function getMarketAsset(assetId) {
  return inMemoryAssets.find((asset) => asset.asset_id === assetId);
}

export function createMarketAsset(asset) {
  const now = new Date().toISOString();
  const newAsset = {
    ...asset,
    asset_id: asset.asset_id || crypto.randomUUID(),
    status: asset.status || "Draft",
    created_by: "Market AI",
    created_at: now,
    updated_at: now,
    version: 1,
    source: "Credit Vivo generated",
    approval_required: true,
    auto_publish_allowed: false,
    uses_stock_assets: false,
  };
  inMemoryAssets.unshift(newAsset);
  return newAsset;
}

export function updateMarketAssetStatus(assetId, status) {
  inMemoryAssets = inMemoryAssets.map((asset) => (asset.asset_id === assetId ? { ...asset, status, updated_at: new Date().toISOString() } : asset));
  return getMarketAsset(assetId);
}
