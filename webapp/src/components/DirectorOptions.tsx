import { useEffect, useState } from "react";
import VisualLookSelectors from "@/components/VisualLookSelectors";
import {
  DIRECTOR_RECIPES,
  RECIPE_CUSTOM_ID,
  directorSummary,
  matchRecipeId,
  readDirectorAdvancedOpen,
  writeDirectorAdvancedOpen,
} from "@/lib/director-recipes";
import { INTRO_PRESETS, STRUCTURE_PRESETS } from "@/lib/prompt-library";
import type { VisualLookValues } from "@/lib/visual-look";
import { emptyVisualLook } from "@/lib/visual-look";

export type DirectorState = {
  structure: string;
  intro: string;
  styleNotes: string;
  visualLook: VisualLookValues;
};

type Props = {
  value: DirectorState;
  onChange: (next: DirectorState) => void;
  aiFootageActive: boolean;
};

export default function DirectorOptions({ value, onChange, aiFootageActive }: Props) {
  const [open, setOpen] = useState(readDirectorAdvancedOpen);
  const [showPacks, setShowPacks] = useState(false);

  const recipeId = matchRecipeId(value.structure, value.intro);
  const summary = directorSummary(value.structure, value.intro, value.styleNotes, recipeId);

  useEffect(() => {
    writeDirectorAdvancedOpen(open);
  }, [open]);

  const setRecipe = (id: string) => {
    if (id === RECIPE_CUSTOM_ID) {
      setShowPacks(true);
      return;
    }
    const r = DIRECTOR_RECIPES.find((x) => x.id === id);
    onChange({
      structure: r?.structure ?? "",
      intro: r?.intro ?? "",
      styleNotes: r?.styleNotes ?? "",
      visualLook: {
        visual_style: r?.visual_style ?? "",
        visual_material: r?.visual_material ?? "",
        visual_tone: r?.visual_tone ?? "",
      },
    });
    setShowPacks(false);
  };

  const patch = (partial: Partial<DirectorState>) => {
    onChange({ ...value, ...partial });
    if (partial.structure !== undefined || partial.intro !== undefined) {
      setShowPacks(true);
    }
  };

  return (
    <div className="rounded-md border border-zinc-800 bg-zinc-950/40">
      <button
        type="button"
        className="w-full flex items-center justify-between gap-2 px-3 py-2.5 text-left text-sm hover:bg-zinc-900/60 rounded-md"
        onClick={() => setOpen((o) => !o)}
      >
        <span className="text-zinc-400">
          Director{" "}
          <span className="text-zinc-600 font-normal">(optional)</span>
        </span>
        <span className="text-xs text-zinc-500 truncate max-w-[55%]">
          {summary ?? "Plain — packs hidden"}
        </span>
        <span className="text-zinc-600 shrink-0">{open ? "▾" : "▸"}</span>
      </button>

      {open && (
        <div className="px-3 pb-4 pt-1 space-y-3 border-t border-zinc-800/80">
          <label className="block text-sm">
            <span className="text-zinc-400">Recipe</span>
            <select
              className="mt-1 w-full rounded-md bg-zinc-950 border border-zinc-700 px-3 py-2 text-sm"
              value={recipeId === RECIPE_CUSTOM_ID ? RECIPE_CUSTOM_ID : recipeId}
              onChange={(e) => setRecipe(e.target.value)}
            >
              {DIRECTOR_RECIPES.map((r) => (
                <option key={r.id || "plain"} value={r.id}>
                  {r.label}
                </option>
              ))}
              <option value={RECIPE_CUSTOM_ID}>Custom mix…</option>
            </select>
            {(() => {
              const r = DIRECTOR_RECIPES.find((x) => x.id === recipeId);
              const blurb =
                r?.blurb ??
                (recipeId === RECIPE_CUSTOM_ID ? "Manual structure / intro below" : "");
              return blurb ? <p className="text-[11px] text-zinc-600 mt-1">{blurb}</p> : null;
            })()}
          </label>

          <button
            type="button"
            className="text-xs text-zinc-500 underline hover:text-zinc-400"
            onClick={() => setShowPacks((s) => !s)}
          >
            {showPacks ? "Hide" : "Show"} all packs ({STRUCTURE_PRESETS.length + INTRO_PRESETS.length - 2} presets)
          </button>

          {showPacks && (
            <div className="space-y-3 pl-2 border-l border-zinc-800">
              <label className="block text-sm">
                <span className="text-zinc-500">Structure</span>
                <select
                  className="mt-1 w-full rounded-md bg-zinc-950 border border-zinc-700 px-3 py-2 text-sm"
                  value={value.structure}
                  onChange={(e) => patch({ structure: e.target.value })}
                >
                  {STRUCTURE_PRESETS.map((s) => (
                    <option key={s.id || "none"} value={s.id}>
                      {s.label}
                    </option>
                  ))}
                </select>
              </label>
              <label className="block text-sm">
                <span className="text-zinc-500">Intro</span>
                <select
                  className="mt-1 w-full rounded-md bg-zinc-950 border border-zinc-700 px-3 py-2 text-sm"
                  value={value.intro}
                  onChange={(e) => patch({ intro: e.target.value })}
                >
                  {INTRO_PRESETS.map((s) => (
                    <option key={s.id || "none"} value={s.id}>
                      {s.label}
                    </option>
                  ))}
                </select>
              </label>
              <label className="block text-sm">
                <span className="text-zinc-500">Style notes</span>
                <input
                  className="mt-1 w-full rounded-md bg-zinc-950 border border-zinc-700 px-3 py-2 text-sm"
                  value={value.styleNotes}
                  onChange={(e) => patch({ styleNotes: e.target.value })}
                  placeholder="Optional hint for the LLM"
                />
              </label>
              <VisualLookSelectors
                value={value.visualLook}
                onChange={(visualLook) => patch({ visualLook })}
                aiFootageActive={aiFootageActive}
              />
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export function directorStateFromNav(partial: {
  structure?: string;
  intro?: string;
  styleNotes?: string;
  visual_style?: string;
  visual_material?: string;
  visual_tone?: string;
}): DirectorState {
  return {
    structure: partial.structure ?? "",
    intro: partial.intro ?? "",
    styleNotes: partial.styleNotes ?? "",
    visualLook: {
      visual_style: partial.visual_style ?? "",
      visual_material: partial.visual_material ?? "",
      visual_tone: partial.visual_tone ?? "",
    },
  };
}

export { emptyVisualLook };
