import { useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  BUILTIN_PROMPTS,
  createPrompt,
  deletePrompt,
  duplicatePrompt,
  isBuiltin,
  listPrompts,
  updatePrompt,
  type PromptKind,
  type SavedPrompt,
} from "@/lib/prompt-library";
import DirectorOptions, { type DirectorState } from "@/components/DirectorOptions";
import { directorSummary, matchRecipeId } from "@/lib/director-recipes";
import { visualLookSummary } from "@/lib/visual-look";

const emptyForm = (): Omit<SavedPrompt, "id" | "createdAt" | "updatedAt"> => ({
  title: "",
  topic: "",
  kind: "short",
  videoType: "explainer",
  structure: "",
  intro: "",
  styleNotes: "",
  visual_style: "",
  visual_material: "",
  visual_tone: "",
});

export default function PromptsPage() {
  const navigate = useNavigate();
  const [tick, setTick] = useState(0);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [form, setForm] = useState(emptyForm);

  const prompts = useMemo(() => listPrompts(), [tick]);

  const refresh = () => setTick((n) => n + 1);

  const startCreate = () => {
    setEditingId("__new__");
    setForm(emptyForm());
  };

  const startEdit = (p: SavedPrompt) => {
    if (isBuiltin(p.id)) {
      setEditingId("__new__");
      setForm({
        title: p.title,
        topic: p.topic,
        kind: p.kind,
        videoType: p.videoType ?? "explainer",
        structure: p.structure ?? "",
        intro: p.intro ?? "",
        styleNotes: p.styleNotes ?? "",
        visual_style: p.visual_style ?? "",
        visual_material: p.visual_material ?? "",
        visual_tone: p.visual_tone ?? "",
      });
      return;
    }
    setEditingId(p.id);
    setForm({
      title: p.title,
      topic: p.topic,
      kind: p.kind,
      videoType: p.videoType ?? "explainer",
      structure: p.structure ?? "",
      intro: p.intro ?? "",
      styleNotes: p.styleNotes ?? "",
      visual_style: p.visual_style ?? "",
      visual_material: p.visual_material ?? "",
      visual_tone: p.visual_tone ?? "",
    });
  };

  const cancelEdit = () => {
    setEditingId(null);
    setForm(emptyForm());
  };

  const saveForm = () => {
    if (!form.title.trim() || !form.topic.trim()) return;
    if (editingId === "__new__") {
      createPrompt({
        title: form.title.trim(),
        topic: form.topic.trim(),
        kind: form.kind,
        videoType: form.kind === "mid" ? form.videoType : undefined,
        structure: form.structure || undefined,
        intro: form.intro || undefined,
        styleNotes: form.styleNotes?.trim() || undefined,
        visual_style: form.visual_style || undefined,
        visual_material: form.visual_material || undefined,
        visual_tone: form.visual_tone || undefined,
      });
    } else if (editingId) {
      updatePrompt(editingId, {
        title: form.title.trim(),
        topic: form.topic.trim(),
        kind: form.kind,
        videoType: form.kind === "mid" ? form.videoType : undefined,
        structure: form.structure || undefined,
        intro: form.intro || undefined,
        styleNotes: form.styleNotes?.trim() || undefined,
        visual_style: form.visual_style || undefined,
        visual_material: form.visual_material || undefined,
        visual_tone: form.visual_tone || undefined,
      });
    }
    cancelEdit();
    refresh();
  };

  const usePrompt = (p: SavedPrompt, target: "generate" | "plan") => {
    const state = {
      topic: p.topic,
      kind: p.kind,
      videoType: p.videoType,
      structure: p.structure,
      intro: p.intro,
      styleNotes: p.styleNotes,
      visual_style: p.visual_style ?? "",
      visual_material: p.visual_material ?? "",
      visual_tone: p.visual_tone ?? "",
    };
    navigate(target === "generate" ? "/generate" : "/plan", { state });
  };

  const directorFromForm = (): DirectorState => ({
    structure: form.structure ?? "",
    intro: form.intro ?? "",
    styleNotes: form.styleNotes ?? "",
    visualLook: {
      visual_style: form.visual_style ?? "",
      visual_material: form.visual_material ?? "",
      visual_tone: form.visual_tone ?? "",
    },
  });

  const setDirectorForm = (d: DirectorState) => {
    setForm({
      ...form,
      structure: d.structure,
      intro: d.intro,
      styleNotes: d.styleNotes,
      visual_style: d.visualLook.visual_style,
      visual_material: d.visualLook.visual_material,
      visual_tone: d.visualLook.visual_tone,
    });
  };

  return (
    <div className="max-w-3xl space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold">Samples</h1>
          <p className="text-sm text-zinc-500 mt-1">
            One-click starters. Plain generate is the default — recipes hide dozens of YAML packs.
          </p>
        </div>
        <button
          type="button"
          onClick={startCreate}
          className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium hover:bg-blue-500"
        >
          New prompt
        </button>
      </div>

      <p className="text-xs text-zinc-600 rounded-md border border-zinc-800 bg-zinc-950/50 px-3 py-2">
        {BUILTIN_PROMPTS.length} built-in samples · Use loads topic + recipe · Director on Generate has 8 curated recipes;
        full trope/intro lists stay behind “Show all packs”.
      </p>

      {editingId && (
        <div className="space-y-4 rounded-lg border border-zinc-700 bg-zinc-900/90 p-5">
          <h2 className="text-sm font-semibold text-zinc-200">
            {editingId === "__new__" ? "Create prompt" : "Edit prompt"}
          </h2>
          <label className="block text-sm">
            <span className="text-zinc-400">Title</span>
            <input
              className="mt-1 w-full rounded-md bg-zinc-950 border border-zinc-700 px-3 py-2 text-sm"
              value={form.title}
              onChange={(e) => setForm({ ...form, title: e.target.value })}
              placeholder="Weekend hike in the Alps"
            />
          </label>
          <label className="block text-sm">
            <span className="text-zinc-400">Topic (sent to LLM)</span>
            <textarea
              className="mt-1 w-full min-h-24 rounded-md bg-zinc-950 border border-zinc-700 px-3 py-2 text-sm"
              value={form.topic}
              onChange={(e) => setForm({ ...form, topic: e.target.value })}
              placeholder="What the video should be about…"
            />
          </label>
          <div className="grid grid-cols-2 gap-3">
            <label className="block text-sm">
              <span className="text-zinc-400">Pipeline</span>
              <select
                className="mt-1 w-full rounded-md bg-zinc-950 border border-zinc-700 px-3 py-2 text-sm"
                value={form.kind}
                onChange={(e) => setForm({ ...form, kind: e.target.value as PromptKind })}
              >
                <option value="short">Short (Generate)</option>
                <option value="mid">Mid-length (Plan)</option>
              </select>
            </label>
            {form.kind === "mid" && (
              <label className="block text-sm">
                <span className="text-zinc-400">Video type</span>
                <select
                  className="mt-1 w-full rounded-md bg-zinc-950 border border-zinc-700 px-3 py-2 text-sm"
                  value={form.videoType}
                  onChange={(e) => setForm({ ...form, videoType: e.target.value })}
                >
                  <option value="explainer">Explainer</option>
                  <option value="tutorial">Tutorial</option>
                  <option value="demo">Demo</option>
                  <option value="documentary">Documentary</option>
                  <option value="showcase">Showcase</option>
                </select>
              </label>
            )}
          </div>
          <DirectorOptions
            value={directorFromForm()}
            onChange={setDirectorForm}
            aiFootageActive
          />
          <div className="flex gap-2">
            <button
              type="button"
              onClick={saveForm}
              disabled={!form.title.trim() || !form.topic.trim()}
              className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium hover:bg-blue-500 disabled:opacity-40"
            >
              Save
            </button>
            <button
              type="button"
              onClick={cancelEdit}
              className="rounded-md border border-zinc-700 px-4 py-2 text-sm hover:bg-zinc-800"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      <ul className="space-y-3">
        {prompts.map((p) => (
          <li
            key={p.id}
            className="rounded-lg border border-zinc-800 bg-zinc-900/60 p-4 flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between"
          >
            <div className="min-w-0 flex-1">
              <div className="flex flex-wrap items-center gap-2">
                <h3 className="font-medium text-zinc-100">{p.title}</h3>
                <span className="text-[10px] uppercase tracking-wide text-zinc-500 border border-zinc-700 rounded px-1.5 py-0.5">
                  {p.kind === "short" ? "short" : "mid"}
                </span>
                {isBuiltin(p.id) && (
                  <span className="text-[10px] text-blue-400/80">sample</span>
                )}
                {(() => {
                  const label = directorSummary(
                    p.structure ?? "",
                    p.intro ?? "",
                    p.styleNotes ?? "",
                    matchRecipeId(p.structure ?? "", p.intro ?? ""),
                  );
                  return label ? (
                    <span className="text-[10px] text-violet-400/90">{label}</span>
                  ) : null;
                })()}
              </div>
              <p className="text-sm text-zinc-400 mt-1 line-clamp-2">{p.topic}</p>
              {p.styleNotes && (
                <p className="text-xs text-zinc-600 mt-1">Notes: {p.styleNotes}</p>
              )}
              {(p.visual_style || p.visual_material || p.visual_tone) && (
                <p className="text-xs text-violet-500/80 mt-1">
                  Look:{" "}
                  {visualLookSummary({
                    visual_style: p.visual_style ?? "",
                    visual_material: p.visual_material ?? "",
                    visual_tone: p.visual_tone ?? "",
                  })}
                </p>
              )}
            </div>
            <div className="flex flex-wrap gap-2 shrink-0">
              <button
                type="button"
                onClick={() => usePrompt(p, p.kind === "short" ? "generate" : "plan")}
                className="rounded-md bg-blue-600/90 px-3 py-1.5 text-xs font-medium hover:bg-blue-500"
              >
                Use
              </button>
              <button
                type="button"
                onClick={() => startEdit(p)}
                className="rounded-md border border-zinc-700 px-3 py-1.5 text-xs hover:bg-zinc-800"
              >
                {isBuiltin(p.id) ? "Copy" : "Edit"}
              </button>
              <button
                type="button"
                onClick={() => {
                  duplicatePrompt(p);
                  refresh();
                }}
                className="rounded-md border border-zinc-700 px-3 py-1.5 text-xs hover:bg-zinc-800"
              >
                Duplicate
              </button>
              {!isBuiltin(p.id) && (
                <button
                  type="button"
                  onClick={() => {
                    deletePrompt(p.id);
                    refresh();
                  }}
                  className="rounded-md border border-red-900/50 text-red-400 px-3 py-1.5 text-xs hover:bg-red-950/40"
                >
                  Delete
                </button>
              )}
            </div>
          </li>
        ))}
      </ul>

      <p className="text-xs text-zinc-600">
        <Link to="/generate" className="text-blue-500 hover:underline">
          Short video
        </Link>
        {" · "}
        <Link to="/plan" className="text-blue-500 hover:underline">
          Mid-length
        </Link>
      </p>
    </div>
  );
}
