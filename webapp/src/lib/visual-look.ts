/** Visual look presets for AI-generated footage (mirrors backend LOOK_CATALOG). */

export type VisualLookValues = {
  visual_style: string;
  visual_material: string;
  visual_tone: string;
};

export const AI_STOCK_PROVIDERS = new Set(["localgen", "cogvideo", "veo", "omni"]);

export const VISUAL_LOOK_CATALOG = {
  styles: [
    { id: "", label: "Default" },
    { id: "cinematic", label: "Cinematic" },
    { id: "documentary", label: "Documentary" },
    { id: "anime", label: "Anime" },
    { id: "surreal", label: "Surreal" },
    { id: "minimalist", label: "Minimalist" },
  ],
  materials: [
    { id: "", label: "Default" },
    { id: "oil_paint", label: "Oil paint" },
    { id: "watercolor", label: "Watercolor" },
    { id: "origami", label: "Origami" },
    { id: "clay", label: "Clay / stop-motion" },
    { id: "pixel", label: "Pixel art" },
    { id: "neon", label: "Neon cyberpunk" },
  ],
  tones: [
    { id: "", label: "Neutral" },
    { id: "somber", label: "Somber" },
    { id: "calm", label: "Calm" },
    { id: "energetic", label: "Energetic" },
    { id: "hilarious", label: "Hilarious" },
  ],
} as const;

export function isAiStockProvider(provider: string): boolean {
  return AI_STOCK_PROVIDERS.has(provider.toLowerCase());
}

export function emptyVisualLook(): VisualLookValues {
  return { visual_style: "", visual_material: "", visual_tone: "" };
}

export function visualLookSummary(look: VisualLookValues): string {
  const parts: string[] = [];
  for (const [key, group] of [
    ["visual_style", VISUAL_LOOK_CATALOG.styles],
    ["visual_material", VISUAL_LOOK_CATALOG.materials],
    ["visual_tone", VISUAL_LOOK_CATALOG.tones],
  ] as const) {
    const id = look[key];
    if (!id) continue;
    const item = group.find((g) => g.id === id);
    if (item) parts.push(item.label);
  }
  return parts.join(" · ") || "Default look";
}
