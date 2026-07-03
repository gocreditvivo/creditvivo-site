import { learningTopics } from "../../../../lib/market/learningTopics";
import { generateLearningStoryboard } from "../../../../lib/market/storyboardGenerator";

export async function POST(request) {
  const body = await request.json();
  const topic = learningTopics.find((item) => item.id === body.topic_id) || learningTopics[0];
  return Response.json({ ok: true, storyboard: generateLearningStoryboard(topic) });
}
