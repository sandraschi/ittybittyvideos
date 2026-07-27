import { useCallback, useEffect, useState } from "react";
import { Download, Eraser, Loader2, Send, Sparkles, Wifi, WifiOff } from "lucide-react";
import { useMutation } from "@tanstack/react-query";
import { generateVideo, planVideo } from "@/lib/api";

const LS_HISTORY = "videogen-chat-history";
const LS_PERSONALITY = "videogen-chat-personality";
const MAX_HISTORY = 100;

type Mode = "short" | "plan";

const PERSONALITIES = [
  { id: "creator", label: "Video Creator", prompt: "You are a video creation expert. Help users generate compelling short-form videos." },
  { id: "director", label: "Creative Director", prompt: "You are a creative director. Focus on storytelling, visual composition, and narrative arc." },
  { id: "analyst", label: "Tech Analyst", prompt: "You are a technical video analyst. Focus on quality, pipeline optimization, and AI model selection." },
  { id: "custom", label: "Custom", prompt: "" },
];

const EXAMPLE_PROMPTS = [
  "A cat walking in a sunny garden",
  "Time-lapse of city traffic",
  "Abstract geometric animation",
  "Nature documentary style clip",
  "Product demo for new gadget",
  "Travel montage of Paris",
  "Cooking tutorial intro",
  "Gaming highlight reel",
  "Explainer video about AI",
];

export default function Chat() {
  const [mode, setMode] = useState<Mode>("short");
  const [input, setInput] = useState("");
  const [log, setLog] = useState<string[]>(() => {
    try { const s = localStorage.getItem(LS_HISTORY); if (s) return JSON.parse(s); } catch { return []; }
    return [];
  });
  const [personality, setPersonality] = useState(() => localStorage.getItem(LS_PERSONALITY) || "creator");
  const [backendOk, setBackendOk] = useState<boolean | null>(null);

  useEffect(() => {
    try { localStorage.setItem(LS_HISTORY, JSON.stringify(log.slice(-MAX_HISTORY))); } catch { /* ignore */ }
  }, [log]);

  useEffect(() => { localStorage.setItem(LS_PERSONALITY, personality); }, [personality]);

  useEffect(() => {
    fetch("/health").then(r => setBackendOk(r.ok)).catch(() => setBackendOk(false));
  }, []);

  const mut = useMutation({
    mutationFn: async (topic: string) => {
      if (mode === "short") {
        const r = await generateVideo({ topic, aspect: "9:16" });
        return `Started short job ${r.job_id} (${r.status})`;
      }
      const r = await planVideo({ topic, target_duration: 180 });
      return `Plan: ${r.storyboard.title} — ${r.storyboard.total_scenes} scenes, ${Math.round(r.storyboard.planned_duration)}s`;
    },
    onSuccess: (msg) => setLog((prev) => [...prev, `\u2192 ${msg}`]),
    onError: (e) => setLog((prev) => [...prev, `\u2717 ${(e as Error).message}`]),
  });

  const handleClear = useCallback(() => {
    setLog([]);
    try { localStorage.removeItem(LS_HISTORY); } catch { /* ignore */ }
  }, []);

  const handleExport = useCallback(() => {
    const text = log.join("\n");
    const blob = new Blob([text], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a"); a.href = url; a.download = `videogen-chat-${new Date().toISOString().slice(0, 10)}.txt`;
    a.click(); URL.revokeObjectURL(url);
  }, [log]);

  return (
    <div data-testid="chat-page" className="max-w-2xl flex flex-col h-[calc(100vh-8rem)]">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h1 className="text-2xl font-bold">Chat</h1>
          <p className="text-sm text-zinc-500">Quick REST bridge — connect MCP client for full tool-calling</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-[10px] uppercase tracking-wider text-zinc-500 font-mono bg-zinc-800 px-2 py-0.5 rounded">skill:video-creator</span>
          <select data-testid="personality-select" value={personality} onChange={(e) => setPersonality(e.target.value)} className="bg-zinc-800 text-xs text-zinc-300 border border-zinc-700 rounded px-2 py-1">
            {PERSONALITIES.map((p) => <option key={p.id} value={p.id}>{p.label}</option>)}
          </select>
          {backendOk === true && <span className="flex items-center gap-1 text-xs text-emerald-400"><Wifi className="w-3 h-3" />Online</span>}
          {backendOk === false && <span className="flex items-center gap-1 text-xs text-red-400"><WifiOff className="w-3 h-3" />Offline</span>}
        </div>
      </div>

      <div className="flex gap-2 mb-3">
        {(["short", "plan"] as Mode[]).map((m) => (
          <button key={m} type="button" onClick={() => setMode(m)} className={`px-3 py-1 rounded text-xs capitalize ${mode === m ? "bg-blue-600" : "bg-zinc-800 text-zinc-400"}`}>{m === "short" ? "Generate short" : "Plan only"}</button>
        ))}
        <div className="flex-1" />
        <div className="flex gap-1">
          <button data-testid="chat-export" onClick={handleExport} disabled={log.length === 0} className="p-1.5 rounded text-zinc-500 hover:text-zinc-300 disabled:opacity-30" title="Export"><Download className="w-3.5 h-3.5" /></button>
          <button data-testid="chat-clear" onClick={handleClear} disabled={log.length === 0} className="p-1.5 rounded text-zinc-500 hover:text-zinc-300 disabled:opacity-30" title="Clear"><Eraser className="w-3.5 h-3.5" /></button>
        </div>
      </div>

      <div data-testid="example-prompts" className="flex flex-wrap gap-1.5 mb-3">
        {EXAMPLE_PROMPTS.map((p) => (
          <button key={p} onClick={() => setInput(p)} className="flex items-center gap-1 px-2 py-1 rounded-full text-[10px] border border-zinc-700 text-zinc-400 hover:text-zinc-200 hover:border-blue-500/40 transition-colors bg-zinc-900/50">
            <Sparkles className="w-2.5 h-2.5" />{p}
          </button>
        ))}
      </div>

      <div data-testid="chat-messages" className="flex-1 overflow-y-auto rounded-lg border border-zinc-800 bg-zinc-900/50 p-4 font-mono text-xs space-y-2 mb-3">
        {log.length === 0 && <p className="text-zinc-600">Enter a topic below\u2026</p>}
        {log.map((line, i) => <p key={i} className="text-zinc-300">{line}</p>)}
      </div>

      <form className="flex gap-2" onSubmit={(e) => { e.preventDefault(); if (!input.trim()) return; setLog((prev) => [...prev, `You: ${input}`]); mut.mutate(input.trim()); setInput(""); }}>
        <input data-testid="chat-input" className="flex-1 rounded-md bg-zinc-950 border border-zinc-700 px-3 py-2 text-sm" value={input} onChange={(e) => setInput(e.target.value)} placeholder="Topic for video\u2026" />
        <button data-testid="chat-send" type="submit" disabled={mut.isPending} className="px-4 py-2 rounded-md bg-blue-600 text-sm font-medium disabled:opacity-40">
          {mut.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
        </button>
      </form>
    </div>
  );
}
