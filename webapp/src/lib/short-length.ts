/** Short-form length = paragraph_count × ~5s clip_duration (backend default). */
export const SHORT_CLIP_SEC = 5;

export type ShortLengthPreset = {
  paragraphs: number;
  label: string;
};

export const SHORT_LENGTH_PRESETS: ShortLengthPreset[] = [
  { paragraphs: 3, label: "~15 sec" },
  { paragraphs: 4, label: "~20 sec" },
  { paragraphs: 5, label: "~25 sec" },
  { paragraphs: 6, label: "~30 sec" },
  { paragraphs: 8, label: "~40 sec" },
  { paragraphs: 10, label: "~50 sec" },
];

export const DEFAULT_SHORT_PARAGRAPHS = 3;

export function shortLengthHint(paragraphs: number): string {
  return `≈ ${paragraphs * SHORT_CLIP_SEC} sec · ${paragraphs} clips`;
}
