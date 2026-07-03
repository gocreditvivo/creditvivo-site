import { learningTopics } from "./learningTopics";
import { generateLearningStoryboard } from "./storyboardGenerator";

export const sampleMarketAssets = learningTopics.map((topic, index) => {
  const storyboard = generateLearningStoryboard(topic);
  return {
    asset_id: `market-demo-${index + 1}`,
    type: "storyboard",
    title: topic.title,
    campaign: "Credit Vivo Learning",
    topic: topic.category,
    format: "9:16",
    status: "Needs Review",
    created_by: "Market AI",
    approved_by: null,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    tags: ["learning", topic.category.toLowerCase().replaceAll(" ", "-"), "credit-vivo"],
    compliance_flags: storyboard.compliance.flags,
    disclosure_included: true,
    source: "Credit Vivo generated",
    version: 1,
    file_path: null,
    thumbnail_path: null,
    transcript_path: null,
    captions_path: null,
    storyboard_path: null,
    storyboard,
    approval_required: true,
    auto_publish_allowed: false,
    uses_stock_assets: false,
  };
});
