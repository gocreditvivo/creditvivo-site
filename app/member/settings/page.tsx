import { SettingsPage } from "@/components/member-portal/MemberPortal";
import { getMemberPortalPayload } from "@/lib/credit-vivo/member-api";

export default async function Page() {
  const payload = await getMemberPortalPayload();
  return <SettingsPage payload={payload} />;
}
