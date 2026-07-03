import { learningTopics } from "../../../../lib/market/learningTopics";
import { generateVideoScript } from "../../../../lib/market/videoScriptGenerator";

export async function POST(request) {
  const body = await request.json();
  const topic = learningTopics.find((item) => item.id === body.topic_id) || learningTopics[0];
  return Response.json({ ok: true, script: generateVideoScript(topic) });
}
