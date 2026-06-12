import type { VisualLookValues } from "@/lib/visual-look";

/** Curated combos — one pick replaces structure + intro + notes. Full pack lists stay in Director advanced. */
export type DirectorRecipe = {
  id: string;
  label: string;
  blurb: string;
  structure?: string;
  intro?: string;
  styleNotes?: string;
} & Partial<VisualLookValues>;

export const DIRECTOR_RECIPES: DirectorRecipe[] = [
  {
    id: "",
    label: "Plain",
    blurb: "Topic only — generic LLM, no packs",
  },
  {
    id: "gsd-food-duo",
    label: "GSD food duo",
    blurb: "Yummy / Whazzat viral pet review",
    structure: "trope:pet-food-duo-review",
    styleNotes: "Fast cuts; optional Yummy / Whazzat labels",
    visual_tone: "hilarious",
  },
  {
    id: "ikea-contrast",
    label: "IKEA × inspirational piano",
    blurb: "Triumph montage, one screw missing",
    structure: "trope:contrast-intro-sequence",
    intro: "intro:ikea-inspirational-piano",
    styleNotes: "Piano never stops; generic flat-pack, not branded",
    visual_tone: "hilarious",
  },
  {
    id: "alpine-mariachi",
    label: "Alpine × mariachi",
    blurb: "Serene village, band slams in loud",
    structure: "trope:contrast-intro-sequence",
    intro: "intro:alpine-mariachi-contrast",
    visual_style: "cinematic",
    visual_tone: "serene",
  },
  {
    id: "bluey-horror",
    label: "Cute × horror audio",
    blurb: "Wholesome visuals, wrong SFX",
    structure: "trope:contrast-intro-sequence",
    intro: "intro:bluey-horror-contrast",
    visual_tone: "hilarious",
  },
  {
    id: "absurd-credits",
    label: "Absurd credits roll",
    blurb: "Pixar-scale fake contributors + stinger",
    structure: "trope:absurd-credits-roll",
    styleNotes: "Einstein + Attila required in credits",
  },
  {
    id: "asmr-demolition",
    label: "ASMR × demolition",
    blurb: "Whisper over car crashes",
    structure: "trope:contrast-intro-sequence",
    intro: "intro:asmr-demolition-contrast",
  },
  {
    id: "nature-toddler",
    label: "Nature doc × birthday",
    blurb: "Attenborough over toddler chaos",
    structure: "trope:contrast-intro-sequence",
    intro: "intro:nature-doc-toddler-chaos",
  },
];

export const RECIPE_CUSTOM_ID = "__custom__";

export function matchRecipeId(structure: string, intro: string): string {
  if (!structure && !intro) return "";
  const hit = DIRECTOR_RECIPES.find(
    (r) =>
      r.id &&
      (r.structure ?? "") === structure &&
      (r.intro ?? "") === intro,
  );
  return hit?.id ?? RECIPE_CUSTOM_ID;
}

export function applyRecipe(recipeId: string): {
  structure: string;
  intro: string;
  styleNotes: string;
  visual: VisualLookValues;
} {
  if (!recipeId || recipeId === RECIPE_CUSTOM_ID) {
    return {
      structure: "",
      intro: "",
      styleNotes: "",
      visual: { visual_style: "", visual_material: "", visual_tone: "" },
    };
  }
  const r = DIRECTOR_RECIPES.find((x) => x.id === recipeId);
  if (!r) {
    return {
      structure: "",
      intro: "",
      styleNotes: "",
      visual: { visual_style: "", visual_material: "", visual_tone: "" },
    };
  }
  return {
    structure: r.structure ?? "",
    intro: r.intro ?? "",
    styleNotes: r.styleNotes ?? "",
    visual: {
      visual_style: r.visual_style ?? "",
      visual_material: r.visual_material ?? "",
      visual_tone: r.visual_tone ?? "",
    },
  };
}

export function directorSummary(
  structure: string,
  intro: string,
  styleNotes: string,
  recipeId?: string,
): string | null {
  if (recipeId && recipeId !== RECIPE_CUSTOM_ID) {
    const r = DIRECTOR_RECIPES.find((x) => x.id === recipeId);
    if (r) return r.label;
  }
  const parts: string[] = [];
  if (structure) parts.push(structure.replace(/^trope:/, ""));
  if (intro) parts.push(intro.replace(/^intro:/, ""));
  if (styleNotes) parts.push("notes");
  if (!parts.length) return null;
  return parts.join(" · ");
}

export const DIRECTOR_STORAGE_KEY = "ittybitty.director-advanced.v1";

export function readDirectorAdvancedOpen(): boolean {
  try {
    return localStorage.getItem(DIRECTOR_STORAGE_KEY) === "1";
  } catch {
    return false;
  }
}

export function writeDirectorAdvancedOpen(open: boolean): void {
  try {
    localStorage.setItem(DIRECTOR_STORAGE_KEY, open ? "1" : "0");
  } catch {
    /* ignore */
  }
}
