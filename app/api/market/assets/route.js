import { listMarketAssets, createMarketAsset } from "../../../../lib/market/assetStorage";

export async function GET() {
  return Response.json({ ok: true, assets: listMarketAssets() });
}

export async function POST(request) {
  const asset = createMarketAsset(await request.json());
  return Response.json({ ok: true, asset });
}
