import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { getStatus, listJobs, probeOllama } from "@/lib/api";

export default function Dashboard() {
  const { data: status } = useQuery({ queryKey: ["status"], queryFn: getStatus, refetchInterval: 8000 });
  const { data: jobs } = useQuery({ queryKey: ["jobs"], queryFn: () => listJobs(5), refetchInterval: 5000 });
  const { data: ollama } = useQuery({ queryKey: ["ollama"], queryFn: probeOllama, staleTime: 30000 });

  const cards = [
    { label: "Jobs total", value: status?.job_count ?? "—", tone: "text-blue-400" },
    { label: "Complete", value: status?.jobs_complete ?? "—", tone: "text-emerald-400" },
    { label: "Active", value: status?.jobs_active ?? "—", tone: "text-amber-400" },
    { label: "MCP tools", value: status?.tool_count ?? "—", tone: "text-violet-400" },
  ];

  return (
    <div className="max-w-4xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <p className="text-sm text-zinc-500 mt-1">roughcut · backend :11054 · dev UI :11055</p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {cards.map((c, i) => (
          <motion.div
            key={c.label}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.05 }}
            className="rounded-lg border border-zinc-800 bg-zinc-900/80 p-4"
          >
            <p className="text-[10px] uppercase tracking-wide text-zinc-500">{c.label}</p>
            <p className={`text-2xl font-semibold mt-1 ${c.tone}`}>{c.value}</p>
          </motion.div>
        ))}
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        <section className="rounded-lg border border-zinc-800 bg-zinc-900/80 p-5">
          <h2 className="font-semibold mb-3">System</h2>
          <ul className="text-sm space-y-2 text-zinc-400">
            <li>
              FFmpeg:{" "}
              <span className={status?.ffmpeg ? "text-emerald-400" : "text-amber-400"}>
                {status?.ffmpeg ? "on PATH" : "missing — install via winget"}
              </span>
            </li>
            <li>
              Whisper align:{" "}
              <span className={status?.align_available ? "text-emerald-400" : "text-zinc-500"}>
                {status?.align_available ? "available" : "uv sync --extra align"}
              </span>
            </li>
            <li>
              Ollama (local LLM):{" "}
              <span className={ollama ? "text-emerald-400" : "text-zinc-500"}>
                {ollama ? ":11434 detected" : "not running"}
              </span>
            </li>
            <li>
              LLM: {status?.providers.llm.join(", ") ?? "—"}
            </li>
            <li>
              Stock: {status?.providers.stock.join(", ") ?? "—"}
            </li>
            <li>
              TTS: {status?.providers.tts.join(", ") ?? "—"}
            </li>
          </ul>
        </section>

        <section className="rounded-lg border border-zinc-800 bg-zinc-900/80 p-5">
          <h2 className="font-semibold mb-3">Quick actions</h2>
          <div className="flex flex-wrap gap-2">
            <Link to="/generate" className="px-3 py-2 rounded-md bg-blue-600 text-sm font-medium hover:bg-blue-500">
              Short video
            </Link>
            <Link to="/plan" className="px-3 py-2 rounded-md bg-zinc-800 text-sm hover:bg-zinc-700 border border-zinc-700">
              Plan mid-length
            </Link>
            <Link to="/publish" className="px-3 py-2 rounded-md bg-zinc-800 text-sm hover:bg-zinc-700 border border-zinc-700">
              Publish
            </Link>
          </div>
        </section>
      </div>

      <section className="rounded-lg border border-zinc-800 bg-zinc-900/80 p-5">
        <h2 className="font-semibold mb-3">Recent jobs</h2>
        {!jobs?.jobs?.length ? (
          <p className="text-sm text-zinc-500">No jobs yet. Start on Generate or Plan.</p>
        ) : (
          <ul className="text-sm divide-y divide-zinc-800">
            {jobs.jobs.map((j) => (
              <li key={j.job_id} className="py-2 flex justify-between gap-4">
                <span className="truncate text-zinc-300">{j.topic || j.job_id}</span>
                <span className="shrink-0 text-zinc-500">
                  {j.status} · {Math.round(j.progress)}%
                </span>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
