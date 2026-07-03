import { generateLearningStoryboard } from "./storyboardGenerator";

export function generateVideoScript(topic) {
  const storyboard = generateLearningStoryboard(topic);
  return {
    title: topic.title,
    duration: topic.duration,
    script: storyboard.scenes.map((scene) => `${scene.time} - ${scene.narration}`).join("\n"),
    captions: storyboard.scenes.map((scene) => scene.narration),
    compliance: storyboard.compliance,
    approval_required: true,
    auto_publish_allowed: false,
  };
}
