export const bannedMarketingPhrases = [
  "guaranteed deletion",
  "guaranteed removal",
  "guaranteed score",
  "guaranteed score increase",
  "delete anything",
  "remove all negative",
  "100% guaranteed",
  "instant credit repair",
  "approved for loan",
  "approved for mortgage",
  "approved for apartment",
  "approved for car loan",
  "lawsuit guaranteed",
  "bureaus must delete",
  "we force deletions",
];

export const preferredMarketingPhrases = [
  "Find errors",
  "Build disputes",
  "Track progress",
  "Review negative accounts",
  "Compare all 3 bureaus",
  "Focused dispute rounds",
  "Clear next steps",
  "Credit improvement is a process",
  "Attorney support may be available for eligible unresolved credit-reporting issues",
];

export function checkMarketingCompliance(text = "") {
  const lower = text.toLowerCase();
  const flags = bannedMarketingPhrases
    .filter((phrase) => lower.includes(phrase.toLowerCase()))
    .map((phrase) => ({
      type: "banned_phrase",
      phrase,
      severity: "high",
      message: `Remove or rewrite banned phrase: ${phrase}`,
    }));

  return {
    ok: flags.length === 0,
    flags,
    approval_required: true,
    auto_publish_allowed: false,
    preferredMarketingPhrases,
  };
}
