import type { VisualLookValues } from "@/lib/visual-look";

export type PromptKind = "short" | "mid";

export type SavedPrompt = {
  id: string;
  title: string;
  topic: string;
  kind: PromptKind;
  videoType?: string;
  /** R10 placeholder — e.g. trope:tutorial */
  structure?: string;
  styleNotes?: string;
  visual_style?: string;
  visual_material?: string;
  visual_tone?: string;
  createdAt: string;
  updatedAt: string;
};

const STORAGE_KEY = "ittybitty.prompt-library.v1";

export const STRUCTURE_PRESETS: { id: string; label: string; note: string }[] = [
  { id: "", label: "(none — generic LLM)", note: "Default today" },
  // Viral exemplars — see docs/EXEMPLARS-RESEARCH.md + templates/tropes/
  { id: "trope:pet-food-duo-review", label: "GSD food duo (Yummy / Whazzat)", note: "Jade-style · 15M+ class" },
  { id: "trope:duo-unfair-portion", label: "Unfair snack / jealousy", note: "Shiba Diva · 61M+ class" },
  { id: "trope:dog-tease-fridge", label: "Dog tease / fake-out foods", note: "Ultimate Dog Tease · 212M+ class" },
  { id: "trope:before-after-reveal", label: "Before / after (result first)", note: "Transformation Short" },
  { id: "trope:satisfying-process-loop", label: "Satisfying process + loop", note: "Clean/build ASMR" },
  { id: "trope:countdown-three-things", label: "3 things countdown", note: "Listicle explainer" },
  { id: "trope:myth-vs-truth", label: "Myth vs truth", note: "Contrarian reveal" },
  { id: "trope:story-hook-reveal", label: "Story hook + late reveal", note: "Interruption / twist" },
  // Narrative (R10 planned)
  { id: "trope:tutorial", label: "Tutorial beats", note: "R10 — backend pending" },
  { id: "trope:documentary", label: "Documentary", note: "R10 — planned" },
  { id: "trope:listicle", label: "Listicle", note: "R10 — planned" },
  { id: "trope:hype-short", label: "Hype short", note: "R10 — planned" },
  { id: "trope:problem-solution", label: "Problem → solution", note: "R10 — planned" },
];

export const BUILTIN_PROMPTS: SavedPrompt[] = [
  {
    id: "sample-vienna-coffee",
    title: "Vienna coffee houses",
    topic: "Why Vienna coffee houses are UNESCO cultural heritage — atmosphere, melange, and slow mornings",
    kind: "short",
    structure: "",
    createdAt: "2026-06-12T00:00:00.000Z",
    updatedAt: "2026-06-12T00:00:00.000Z",
  },
  {
    id: "sample-gsd-food-duo",
    title: "GSD food duo — Yummy vs Whazzat",
    topic: "Two German shepherds taste the same treats — one eats everything, one side-eyes every morsel like whazzat",
    kind: "short",
    structure: "trope:pet-food-duo-review",
    visual_material: "",
    visual_tone: "hilarious",
    styleNotes: "Floating Yummy / Whazzat labels; 1.5s cuts; Jellyfin GSD footage",
    createdAt: "2026-06-12T00:00:00.000Z",
    updatedAt: "2026-06-12T00:00:00.000Z",
  },
  {
    id: "sample-sourdough",
    title: "Sourdough starter basics",
    topic: "How to keep a sourdough starter alive for beginners — feeding schedule, smell checks, and common mistakes",
    kind: "mid",
    videoType: "tutorial",
    structure: "trope:countdown-three-things",
    styleNotes: "3 mistakes beginners make — expand to full tutorial chapters",
    createdAt: "2026-06-12T00:00:00.000Z",
    updatedAt: "2026-06-12T00:00:00.000Z",
  },
  {
    id: "sample-quantum",
    title: "Quantum computing primer",
    topic: "Quantum computing explained for curious non-physicists — qubits, superposition, and why it is not magic",
    kind: "mid",
    videoType: "explainer",
    structure: "trope:problem-solution",
    createdAt: "2026-06-12T00:00:00.000Z",
    updatedAt: "2026-06-12T00:00:00.000Z",
  },
  {
    id: "sample-cat-shorts",
    title: "Cats are amazing",
    topic: "Three surprising facts about house cats that make them perfect apartment pets",
    kind: "short",
    visual_material: "origami",
    visual_tone: "hilarious",
    createdAt: "2026-06-12T00:00:00.000Z",
    updatedAt: "2026-06-12T00:00:00.000Z",
  },
];

function newId(): string {
  return `user-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
}

function readUserPrompts(): SavedPrompt[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw) as SavedPrompt[];
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function writeUserPrompts(prompts: SavedPrompt[]): void {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(prompts));
}

/** Built-in samples + user-created (user ids never collide with sample-*). */
export function listPrompts(): SavedPrompt[] {
  const user = readUserPrompts();
  const builtinIds = new Set(BUILTIN_PROMPTS.map((p) => p.id));
  const merged = [
    ...BUILTIN_PROMPTS,
    ...user.filter((p) => !builtinIds.has(p.id)),
  ];
  return merged.sort((a, b) => a.title.localeCompare(b.title));
}

export function isBuiltin(id: string): boolean {
  return id.startsWith("sample-");
}

export function createPrompt(
  input: Omit<SavedPrompt, "id" | "createdAt" | "updatedAt">,
): SavedPrompt {
  const now = new Date().toISOString();
  const prompt: SavedPrompt = { ...input, id: newId(), createdAt: now, updatedAt: now };
  writeUserPrompts([...readUserPrompts(), prompt]);
  return prompt;
}

export function updatePrompt(id: string, patch: Partial<Omit<SavedPrompt, "id" | "createdAt">>): SavedPrompt | null {
  if (isBuiltin(id)) return null;
  const user = readUserPrompts();
  const idx = user.findIndex((p) => p.id === id);
  if (idx < 0) return null;
  const updated: SavedPrompt = {
    ...user[idx],
    ...patch,
    id,
    updatedAt: new Date().toISOString(),
  };
  user[idx] = updated;
  writeUserPrompts(user);
  return updated;
}

export function deletePrompt(id: string): boolean {
  if (isBuiltin(id)) return false;
  const next = readUserPrompts().filter((p) => p.id !== id);
  if (next.length === readUserPrompts().length) return false;
  writeUserPrompts(next);
  return true;
}

export function duplicatePrompt(source: SavedPrompt): SavedPrompt {
  return createPrompt({
    title: `${source.title} (copy)`,
    topic: source.topic,
    kind: source.kind,
    videoType: source.videoType,
    structure: source.structure,
    styleNotes: source.styleNotes,
    visual_style: source.visual_style,
    visual_material: source.visual_material,
    visual_tone: source.visual_tone,
  });
}

export type PromptNavState = {
  topic: string;
  kind?: PromptKind;
  videoType?: string;
  structure?: string;
  styleNotes?: string;
} & VisualLookValues;
