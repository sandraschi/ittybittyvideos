import {
  VISUAL_LOOK_CATALOG,
  type VisualLookValues,
  visualLookSummary,
} from "@/lib/visual-look";

type Props = {
  value: VisualLookValues;
  onChange: (next: VisualLookValues) => void;
  /** When false, show compact note that look applies only to AI footage providers. */
  aiFootageActive: boolean;
};

const selectClass =
  "mt-1 w-full rounded-md bg-zinc-950 border border-zinc-700 px-3 py-2 text-sm";

export default function VisualLookSelectors({ value, onChange, aiFootageActive }: Props) {
  const set = (patch: Partial<VisualLookValues>) => onChange({ ...value, ...patch });

  return (
    <fieldset className="space-y-3 rounded-md border border-violet-900/40 bg-violet-950/15 p-4">
      <legend className="px-1 text-sm font-medium text-violet-200">AI footage look</legend>
      {!aiFootageActive ? (
        <p className="text-xs text-zinc-500">
          Applies when Settings → Footage is <strong className="text-zinc-400">LocalGen</strong>,{" "}
          <strong className="text-zinc-400">Veo</strong>, or <strong className="text-zinc-400">Omni</strong>. Pexels /
          library clips ignore these.
        </p>
      ) : (
        <p className="text-xs text-emerald-500/90">Appended to each AI clip prompt.</p>
      )}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <label className="block text-sm">
          <span className="text-zinc-400">Style</span>
          <select
            className={selectClass}
            value={value.visual_style}
            onChange={(e) => set({ visual_style: e.target.value })}
          >
            {VISUAL_LOOK_CATALOG.styles.map((o) => (
              <option key={o.id || "default"} value={o.id}>
                {o.label}
              </option>
            ))}
          </select>
        </label>
        <label className="block text-sm">
          <span className="text-zinc-400">Material</span>
          <select
            className={selectClass}
            value={value.visual_material}
            onChange={(e) => set({ visual_material: e.target.value })}
          >
            {VISUAL_LOOK_CATALOG.materials.map((o) => (
              <option key={o.id || "default"} value={o.id}>
                {o.label}
              </option>
            ))}
          </select>
        </label>
        <label className="block text-sm">
          <span className="text-zinc-400">Tone</span>
          <select
            className={selectClass}
            value={value.visual_tone}
            onChange={(e) => set({ visual_tone: e.target.value })}
          >
            {VISUAL_LOOK_CATALOG.tones.map((o) => (
              <option key={o.id || "default"} value={o.id}>
                {o.label}
              </option>
            ))}
          </select>
        </label>
      </div>
      <p className="text-[11px] text-zinc-600">
        Preview: {visualLookSummary(value)}
        {aiFootageActive && value.visual_material === "origami" && " — folded-paper prompts"}
      </p>
    </fieldset>
  );
}
