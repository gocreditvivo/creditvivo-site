export default function VideoStoryboardCard({ scene }) {
  return <article className="creative-card"><strong>{scene.headline}</strong><p>{scene.time}</p><p>{scene.visual}</p></article>;
}
