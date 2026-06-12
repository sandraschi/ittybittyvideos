import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useLocation, useNavigate } from "react-router-dom";
import VisualLookSelectors from "@/components/VisualLookSelectors";
import { generateVideo, getSettings, getStatus } from "@/lib/api";
import type { PromptNavState } from "@/lib/prompt-library";
import { emptyVisualLook, isAiStockProvider } from "@/lib/visual-look";
import { useJobsStore } from "@/store/jobs";

type GenerateMode = "deepseek" | "openai" | "lmstudio" | "ollama" | "script";

const SAMPLE_SCRIPT = `Cats are fascinating companions. They sleep up to sixteen hours a day and still find time to judge you.

Their purring may help heal bones and reduce stress in humans. Science still argues about why they purr.

Every cat has a unique nose print, like a human fingerprint. No two toe beans are alike.`;

function modeLabel(mode: GenerateMode): string {
  if (mode === "deepseek") return "DeepSeek topic";
  if (mode === "openai") return "OpenAI topic";
  if (mode === "lmstudio") return "LM Studio topic";
  if (mode === "ollama") return "Ollama topic";
  return "Custom script";
}

function modeReady(
  mode: GenerateMode,
  llm?: {
    deepseek_ready?: boolean;
    openai_ready?: boolean;
    lmstudio_ready?: boolean;
    ollama_ready?: boolean;
  }
): boolean {
  if (mode === "script") return true;
  if (mode === "deepseek") return llm?.deepseek_ready ?? false;
  if (mode === "openai") return llm?.openai_ready ?? false;
  if (mode === "lmstudio") return llm?.lmstudio_ready ?? false;
  return llm?.ollama_ready ?? false;
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
  const [paragraphs, setParagraphs] = useState(3);
  const [fromLibrary, setFromLibrary] = useState<string | null>(null);
  const [visualLook, setVisualLook] = useState(emptyVisualLook);

  const { data: settings } = useQuery({ queryKey: ["settings"], queryFn: getSettings });
  const stockProvider = settings?.settings.videogen_stock_provider ?? "pexels";

  useEffect(() => {
    const s = location.state as PromptNavState | null;
    if (!s?.topic) return;
    setTopic(s.topic);
    setFromLibrary(s.topic.slice(0, 48));
    setVisualLook({
      visual_style: s.visual_style ?? "",
      visual_material: s.visual_material ?? "",
      visual_tone: s.visual_tone ?? "",
    });
    navigate(location.pathname, { replace: true, state: null });
  }, [location.pathname, location.state, navigate]);

  const { data: status } = useQuery({ queryKey: ["status"], queryFn: getStatus, refetchInterval: 15_000 });
  const llm = status?.llm;

  useEffect(() => {
    if (!llm) return;
    if (modeReady(mode, llm)) return;
    if (llm.deepseek_ready) setMode("deepseek");
    else if (llm.openai_ready) setMode("openai");
    else if (llm.lmstudio_ready) setMode("lmstudio");
    else if (llm.ollama_ready) setMode("ollama");
    else setMode("script");
  }, [llm, mode]);

  const mutation = useMutation({
    mutationFn: () => {
      if (mode === "script") {
        return generateVideo({
          script: script.trim(),
          aspect,
          paragraph_count: paragraphs,
          clip_duration: 5,
        });
      }
      return generateVideo({
        topic: topic.trim(),
        llm_provider: mode,
        aspect,
        paragraph_count: paragraphs,
        clip_duration: 5,
        ...visualLook,
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

  const deepseekModel = llm?.deepseek_model ?? "deepseek-v4-flash";
  const lmstudioLabel = llm?.lmstudio_model ? `${llm.lmstudio_model} · local` : ":1234 · local";

  const modeBtn = (m: GenerateMode, subtitle: string) => {
    const on = mode === m;
    const ok = modeReady(m, llm);
    return (
      <button
        key={m}
        type="button"
        className={`flex-1 min-w-[7rem] rounded-md py-2 px-2 border text-left ${on ? "border-blue-500 bg-blue-950/50" : "border-zinc-700"}`}
        onClick={() => setMode(m)}
      >
        <span className="block text-sm font-medium">{modeLabel(m)}</span>
        <span className={`block text-xs mt-0.5 ${ok ? "text-emerald-400" : "text-amber-400"}`}>
          {m === "script" ? "No LLM" : ok ? "Ready" : "Not configured"}
        </span>
        <span className="block text-[10px] text-zinc-500 mt-0.5">{subtitle}</span>
      </button>
    );
  };

  return (
    <div className="max-w-xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Short video</h1>
        <p className="text-sm text-zinc-500 mt-1">
          30–60s · pick scripting source ·{" "}
          <Link to="/prompts" className="text-blue-500 hover:underline">
            Prompt library
          </Link>
        </p>
        {fromLibrary && (
          <p className="text-xs text-emerald-500/90 mt-1">Loaded from prompt library</p>
        )}
      </div>

      <form
        className="space-y-4 rounded-lg border border-zinc-800 bg-zinc-900/80 p-5"
        onSubmit={(e) => {
          e.preventDefault();
          mutation.mutate();
        }}
      >
        <div className="flex flex-wrap gap-2 text-sm">
          {modeBtn("deepseek", `${deepseekModel} · cloud`)}
          {modeBtn("openai", "gpt-4o-mini · cloud")}
          {modeBtn("lmstudio", lmstudioLabel)}
          {modeBtn("ollama", "llama3.2:3b · local")}
          {modeBtn("script", "Paste narration")}
        </div>

        {!ready && mode !== "script" && (
          <p className="text-sm text-amber-300 rounded-md border border-amber-800/50 bg-amber-950/30 px-3 py-2">
            {mode === "deepseek"
              ? "Set DEEPSEEK_API_KEY in .env and restart the backend."
              : mode === "openai"
                ? "Set OPENAI_API_KEY in .env and restart the backend."
                : mode === "lmstudio"
                  ? "Open LM Studio, load a model, enable server on :1234."
                  : "Start Ollama on :11434 (ollama pull llama3.2:3b)."}
          </p>
        )}

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
            <span className="text-zinc-400">
              Topic ·{" "}
              {mode === "deepseek"
                ? "DeepSeek V4 Flash"
                : mode === "openai"
                  ? "OpenAI"
                  : mode === "lmstudio"
                    ? "LM Studio"
                    : "Ollama"}{" "}
              writes the script
            </span>
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
            <span className="text-zinc-400">Aspect</span>
            <select
              className="mt-1 w-full rounded-md bg-zinc-950 border border-zinc-700 px-3 py-2 text-sm"
              value={aspect}
              onChange={(e) => setAspect(e.target.value)}
            >
              <option value="9:16">9:16 (vertical)</option>
              <option value="16:9">16:9 (landscape)</option>
              <option value="1:1">1:1</option>
            </select>
          </label>
          <label className="block text-sm">
            <span className="text-zinc-400">Segments</span>
            <input
              type="number"
              min={1}
              max={10}
              className="mt-1 w-full rounded-md bg-zinc-950 border border-zinc-700 px-3 py-2 text-sm"
              value={paragraphs}
              onChange={(e) => setParagraphs(Number(e.target.value))}
            />
          </label>
        </div>

        <VisualLookSelectors
          value={visualLook}
          onChange={setVisualLook}
          aiFootageActive={isAiStockProvider(stockProvider)}
        />

        <button
          type="submit"
          disabled={mutation.isPending || !canSubmit}
          className="w-full py-2.5 rounded-md bg-blue-600 font-medium text-sm hover:bg-blue-500 disabled:opacity-40"
        >
          {mutation.isPending ? "Starting…" : `Generate · ${modeLabel(mode)}`}
        </button>
        {mutation.isError && (
          <p className="text-sm text-red-400">{(mutation.error as Error).message}</p>
        )}
      </form>
    </div>
  );
}
