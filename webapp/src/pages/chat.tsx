import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { generateVideo, planVideo } from "@/lib/api";

type Mode = "short" | "plan";

export default function Chat() {
  const [mode, setMode] = useState<Mode>("short");
  const [input, setInput] = useState("");
  const [log, setLog] = useState<string[]>([]);

  const mut = useMutation({
    mutationFn: async (topic: string) => {
      if (mode === "short") {
        const r = await generateVideo({ topic, aspect: "9:16" });
        return `Started short job ${r.job_id} (${r.status})`;
      }
      const r = await planVideo({ topic, target_duration: 180 });
      return `Plan: ${r.storyboard.title} — ${r.storyboard.total_scenes} scenes, ${Math.round(r.storyboard.planned_duration)}s`;
    },
    onSuccess: (msg) => setLog((prev) => [...prev, `→ ${msg}`]),
    onError: (e) => setLog((prev) => [...prev, `✗ ${(e as Error).message}`]),
  });

  return (
    <div className="max-w-2xl flex flex-col h-[calc(100vh-8rem)]">
      <div className="mb-4">
        <h1 className="text-2xl font-bold">Chat</h1>
        <p className="text-sm text-zinc-500">Quick REST bridge — connect MCP client for full tool-calling</p>
      </div>

      <div className="flex gap-2 mb-3">
        {(["short", "plan"] as Mode[]).map((m) => (
          <button
            key={m}
            type="button"
            onClick={() => setMode(m)}
            className={`px-3 py-1 rounded text-xs capitalize ${
              mode === m ? "bg-blue-600" : "bg-zinc-800 text-zinc-400"
            }`}
          >
            {m === "short" ? "Generate short" : "Plan only"}
          </button>
        ))}
      </div>

      <div className="flex-1 overflow-y-auto rounded-lg border border-zinc-800 bg-zinc-900/50 p-4 font-mono text-xs space-y-2 mb-3">
        {log.length === 0 && <p className="text-zinc-600">Enter a topic below…</p>}
        {log.map((line, i) => (
          <p key={i} className="text-zinc-300">
            {line}
          </p>
        ))}
      </div>

      <form
        className="flex gap-2"
        onSubmit={(e) => {
          e.preventDefault();
          if (!input.trim()) return;
          setLog((prev) => [...prev, `You: ${input}`]);
          mut.mutate(input.trim());
          setInput("");
        }}
      >
        <input
          className="flex-1 rounded-md bg-zinc-950 border border-zinc-700 px-3 py-2 text-sm"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Topic for video…"
        />
        <button
          type="submit"
          disabled={mut.isPending}
          className="px-4 py-2 rounded-md bg-blue-600 text-sm font-medium disabled:opacity-40"
        >
          Send
        </button>
      </form>
    </div>
  );
}
