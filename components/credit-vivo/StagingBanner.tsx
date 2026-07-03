import { STAGING_BANNER_TEXT, STAGING_RULES } from "@/lib/credit-vivo/staging";

export function StagingBanner() {
  if (!STAGING_RULES.isStaging) {
    return null;
  }

  return (
    <div className="border-b border-amber-300 bg-amber-50 px-4 py-3 text-center text-sm font-bold text-amber-900">
      {STAGING_BANNER_TEXT}
    </div>
  );
}

