import { creditVivoBrandKit } from "./brandKit";
import { checkMarketingCompliance } from "./complianceRules";

export function generateLearningStoryboard(topic) {
  const sceneData = [
    [1, "0:00-0:15", topic.hook, "Animated Credit Vivo dashboard opening", "Soft zoom, bureau cards slide in", topic.hook],
    [2, "0:15-0:30", "Start with your reports", "Three bureau cards: Equifax, Experian, TransUnion", "Cards stack into scanner", "Credit reports can show different details across the three bureaus."],
    [3, "0:30-0:45", "Credit Vivo scans for review", "AI scan animation over report cards", "Scanner beam highlights negative accounts", "Credit Vivo helps organize possible issues for review."],
    [4, "0:45-1:00", "Compare the bureaus", "3-bureau comparison table", "Rows highlight balance, status, date", "The scanner compares balances, statuses, dates, and account details."],
    [5, "1:00-1:15", "Focus on negative accounts", "Negative account cards sort by issue type", "Cards move into categories", "Collections and charge-offs need careful field-level review."],
    [6, "1:15-1:30", "Build focused rounds", "Round 1, Round 2, Follow-up timeline", "Timeline animates left to right", "Focused dispute rounds help keep the process organized."],
    [7, "1:30-1:45", "Attach the proof", "Packet layers: letter, comparison, report pages, evidence", "Layers stack into a packet", "A strong packet includes the letter, comparison, report pages, and evidence."],
    [8, "1:45-2:00", "Customer approval", "Review and approve button", "Tap animation", "Customers review and approve before anything is mailed."],
    [9, "2:00-2:15", "Track every step", "Mail tracking timeline", "Mailed, delivered, response due", "Credit Vivo tracks delivery, deadlines, responses, and follow-ups."],
    [10, "2:15-2:30", "Refresh your scan", "Upload new report cards", "New upload compares to old scan", "Refresh your reports to see what changed."],
    [11, "2:30-2:45", "Know the next step", "Dashboard next-step card", "Next step slides into view", "The dashboard shows the next step clearly."],
    [12, "2:45-3:00", creditVivoBrandKit.trustLine, "Credit Vivo logo and final dashboard", "Clean brand end card", `${creditVivoBrandKit.trustLine}. ${creditVivoBrandKit.slogan}.`],
  ];
  const scenes = sceneData.map(([scene, time, headline, visual, motion, narration]) => ({ scene, time, headline, visual, motion, narration }));
  return {
    topic_id: topic.id,
    title: topic.title,
    duration: topic.duration,
    brand: creditVivoBrandKit.brandName,
    scenes,
    compliance: checkMarketingCompliance(JSON.stringify(scenes)),
    source: "Credit Vivo generated",
    uses_stock_assets: false,
    auto_publish_allowed: false,
  };
}
