import { MessagesPage } from "@/components/member-portal/MemberPortal";
import { getMemberPortalPayload } from "@/lib/credit-vivo/member-api";

export default async function Page() {
  const payload = await getMemberPortalPayload();
  return <MessagesPage payload={payload} />;
}
