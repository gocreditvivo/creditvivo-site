export function generateImagePrompt(template) {
  return `Credit Vivo-owned ${template.visual} creative, ${template.size || template.format}, headline: ${template.headline || template.title}, no stock footage, no competitor visuals.`;
}
