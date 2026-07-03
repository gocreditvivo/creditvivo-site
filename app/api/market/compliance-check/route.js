import { checkMarketingCompliance } from "../../../../lib/market/complianceRules";

export async function POST(request) {
  const body = await request.json();
  return Response.json(checkMarketingCompliance(body.text || ""));
}
