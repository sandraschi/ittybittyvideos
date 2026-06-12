import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useLocation, useNavigate } from "react-router-dom";
import DirectorOptions, {
  directorStateFromNav,
  emptyVisualLook,
  type DirectorState,
} from "@/components/DirectorOptions";
import { directorSummary, matchRecipeId } from "@/lib/director-recipes";
import { generateVideo, getSettings, getStatus } from "@/lib/api";
import type { PromptNavState } from "@/lib/prompt-library";
import {
  DEFAULT_SHORT_PARAGRAPHS,
  SHORT_CLIP_SEC,
  SHORT_LENGTH_PRESETS,
  shortLengthHint,
} from "@/lib/short-length";
import { isAiStockProvider } from "@/lib/visual-look";
import { useJobsStore } from "@/store/jobs";

type GenerateMode = "deepseek" | "openai" | "lmstudio" | "ollama" | "script";

const SAMPLE_SCRIPT = `Cats are fascinating companions. They sleep up to sixteen hours a day and still find time to judge you.

Their purring may help heal bones and reduce stress in humans. Science still argues about why they purr.

Every cat has a unique nose print, like a human fingerprint. No two toe beans are alike.`;

function modeLabel(mode: GenerateMode): string {
  if (mode === "deepseek") return "DeepSeek";
  if (mode === "openai") return "OpenAI";
  if (mode === "lmstudio") return "LM Studio";
  if (mode === "ollama") return "Ollama";
  return "Custom script";
}

function modeReady(
  mode: GenerateMode,
  llm?: {
    deepseek_ready?: boolean;
    openai_ready?: boolean;
    lmstudio_ready?: boolean;
    ollama_ready?: boolean;
  },
): boolean {
  if (mode === "script") return true;
  if (mode === "deepseek") return llm?.deepseek_ready ?? false;
  if (mode === "openai") return llm?.openai_ready ?? false;
  if (mode === "lmstudio") return llm?.lmstudio_ready ?? false;
  return llm?.ollama_ready ?? false;
}

function pickDefaultMode(llm?: Parameters<typeof modeReady>[1]): GenerateMode {
  if (llm?.deepseek_ready) return "deepseek";
  if (llm?.openai_ready) return "openai";
  if (llm?.lmstudio_ready) return "lmstudio";
  if (llm?.ollama_ready) return "ollama";
  return "script";
}

export default function Generate() {
  const navigate = useNavigate();
  const location = useLocation();
  const qc = useQueryClient();
  const setActiveJobId = useJobsStore((s) => s.setActiveJobId);
  const [mode, setMode] = useState<GenerateMode>("deepseek");
  const [topic, setTopic] = useState("");
  const [script, setScript] = useState("");
  const [aspect, setAspect] = useState("9:16");
  const [paragraphs, setParagraphs] = useState(DEFAULT_SHORT_PARAGRAPHS);
  const [fromLibrary, setFromLibrary] = useState(false);
  const [director, setDirector] = useState<DirectorState>({
    structure: "",
    intro: "",
    styleNotes: "",
    visualLook: emptyVisualLook(),
  });

  const { data: settings } = useQuery({ queryKey: ["settings"], queryFn: getSettings });
  const stockProvider = settings?.settings.videogen_stock_provider ?? "pexels";

  useEffect(() => {
    const s = location.state as PromptNavState | null;
    if (!s?.topic) return;
    setTopic(s.topic);
    setFromLibrary(true);
    setDirector(directorStateFromNav(s));
    navigate(location.pathname, { replace: true, state: null });
  }, [location.pathname, location.state, navigate]);

  const { data: status } = useQuery({ queryKey: ["status"], queryFn: getStatus, refetchInterval: 15_000 });
  const llm = status?.llm;

  useEffect(() => {
    if (!llm) return;
    if (modeReady(mode, llm)) return;
    setMode(pickDefaultMode(llm));
  }, [llm, mode]);

  const mutation = useMutation({
    mutationFn: () => {
      if (mode === "script") {
        return generateVideo({
          script: script.trim(),
          aspect,
          paragraph_count: paragraphs,
          clip_duration: SHORT_CLIP_SEC,
        });
      }
      return generateVideo({
        topic: topic.trim(),
        llm_provider: mode,
        aspect,
        paragraph_count: paragraphs,
        clip_duration: SHORT_CLIP_SEC,
        structure: director.structure || undefined,
        style_notes: director.styleNotes || undefined,
        intro: director.intro || undefined,
        ...director.visualLook,
      });
    },
    onSuccess: (data) => {
      setActiveJobId(data.job_id);
      qc.invalidateQueries({ queryKey: ["jobs"] });
      navigate(`/jobs?highlight=${data.job_id}`);
    },
  });

  const ready = modeReady(mode, llm);
  const canSubmit =
    mode === "script" ? script.trim().length > 20 : topic.trim().length > 0 && ready;

  const recipeLabel = directorSummary(
    director.structure,
    director.intro,
    director.styleNotes,
    matchRecipeId(director.structure, director.intro),
  );

  return (
    <div className="max-w-xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Short video</h1>
        <p className="text-sm text-zinc-500 mt-1">
          Topic · length · aspect → generate. Packs under Director (optional).{" "}
          <Link to="/prompts" className="text-blue-500 hover:underline">
            Samples
          </Link>
        </p>
        {fromLibrary && (
          <p className="text-xs text-emerald-500/90 mt-1">
            Loaded from library{recipeLabel ? ` · ${recipeLabel}` : ""}
          </p>
        )}
      </div>

      <form
        className="space-y-4 rounded-lg border border-zinc-800 bg-zinc-900/80 p-5"
        onSubmit={(e) => {
          e.preventDefault();
          mutation.mutate();
        }}
      >
        {mode === "script" ? (
          <label className="block text-sm">
            <span className="text-zinc-400">Script (blank line between segments)</span>
            <textarea
              className="mt-1 w-full min-h-40 rounded-md bg-zinc-950 border border-zinc-700 px-3 py-2 text-sm focus:border-blue-500 outline-none font-mono"
              value={script}
              onChange={(e) => setScript(e.target.value)}
              placeholder={SAMPLE_SCRIPT}
              required
            />
            <button
              type="button"
              className="mt-2 text-xs text-zinc-500 underline"
              onClick={() => setScript(SAMPLE_SCRIPT)}
            >
              Load sample script
            </button>
          </label>
        ) : (
          <label className="block text-sm">
            <span className="text-zinc-400">Topic</span>
            <input
              className="mt-1 w-full rounded-md bg-zinc-950 border border-zinc-700 px-3 py-2 text-sm focus:border-blue-500 outline-none"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="Why cats are amazing pets"
              required
            />
          </label>
        )}

        <div className="grid grid-cols-2 gap-3">
          <label className="block text-sm">
            <span className="text-zinc-400">Length</span>
            <select
              className="mt-1 w-full rounded-md bg-zinc-950 border border-zinc-700 px-3 py-2 text-sm"
              value={paragraphs}
              onChange={(e) => setParagraphs(Number(e.target.value))}
            >
              {SHORT_LENGTH_PRESETS.map((p) => (
                <option key={p.paragraphs} value={p.paragraphs}>
                  {p.label}
                </option>
              ))}
            </select>
            <span className="text-[11px] text-zinc-600 mt-0.5 block">{shortLengthHint(paragraphs)}</span>
          </label>
          <label className="block text-sm">
            <span className="text-zinc-400">Aspect</span>
            <select
              className="mt-1 w-full rounded-md bg-zinc-950 border border-zinc-700 px-3 py-2 text-sm"
              value={aspect}
              onChange={(e) => setAspect(e.target.value)}
            >
              <option value="9:16">9:16 vertical</option>
              <option value="16:9">16:9 landscape</option>
            </select>
          </label>
        </div>

        <DirectorOptions
          value={director}
          onChange={setDirector}
          aiFootageActive={isAiStockProvider(stockProvider)}
        />

        <details className="text-sm text-zinc-500">
          <summary className="cursor-pointer hover:text-zinc-400">Script source · {modeLabel(mode)}</summary>
          <div className="mt-2 flex flex-wrap gap-2">
            {(["deepseek", "openai", "lmstudio", "ollama", "script"] as GenerateMode[]).map((m) => (
              <button
                key={m}
                type="button"
                className={`rounded-md px-2 py-1 text-xs border ${mode === m ? "border-blue-500 text-blue-300" : "border-zinc-700"}`}
                onClick={() => setMode(m)}
              >
                {modeLabel(m)}
              </button>
            ))}
          </div>
          {!ready && mode !== "script" && (
            <p className="mt-2 text-xs text-amber-300">Configure {modeLabel(mode)} in Settings / .env</p>
          )}
        </details>

        <button
          type="submit"
          disabled={mutation.isPending || !canSubmit}
          className="w-full py-2.5 rounded-md bg-blue-600 font-medium text-sm hover:bg-blue-500 disabled:opacity-40"
        >
          {mutation.isPending ? "Starting…" : "Generate"}
        </button>
        {mutation.isError && (
          <p className="text-sm text-red-400">{(mutation.error as Error).message}</p>
        )}
      </form>
    </div>
  );
}
