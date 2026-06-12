import { useState } from "react";
import { useSearchParams } from "react-router-dom";
import { useQuery, useMutation } from "@tanstack/react-query";
import { Copy, ExternalLink, FolderOpen, Download } from "lucide-react";
import { getPublishPack, listDepot, revealJob } from "@/lib/api";

export default function Publish() {
  const [params, setParams] = useSearchParams();
  const jobId = params.get("job") ?? "";
  const [copied, setCopied] = useState(false);

  const { data: depot } = useQuery({ queryKey: ["depot"], queryFn: () => listDepot(50) });
  const completeJobs =
    depot?.items.filter((j) => j.has_file && j.status === "complete") ?? [];

  const { data: pack } = useQuery({
    queryKey: ["publish", jobId],
    queryFn: () => getPublishPack(jobId),
    enabled: Boolean(jobId),
  });

  const revealMut = useMutation({
    mutationFn: () => revealJob(jobId),
  });

  const copyCaption = async () => {
    if (!pack?.caption) return;
    await navigator.clipboard.writeText(pack.caption);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="max-w-3xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Publish</h1>
        <p className="text-sm text-zinc-500 mt-1">
          Minimum fuss: download → copy caption → open platform upload. No OAuth circus (yet).
        </p>
      </div>

      <section className="rounded-lg border border-zinc-800 bg-zinc-900/80 p-4">
        <label className="text-sm text-zinc-400">Completed job</label>
        <select
          className="mt-1 w-full rounded-md bg-zinc-950 border border-zinc-700 px-3 py-2 text-sm"
          value={jobId}
          onChange={(e) => setParams(e.target.value ? { job: e.target.value } : {})}
        >
          <option value="">Select a job…</option>
          {completeJobs.map((j) => (
            <option key={j.job_id} value={j.job_id}>
              {j.topic || j.job_id}
            </option>
          ))}
        </select>
      </section>

      {pack && pack.ready && (
        <>
          <section className="rounded-lg border border-zinc-800 bg-zinc-900/80 p-5 space-y-4">
            <h2 className="font-semibold">Handoff pack</h2>
            <textarea
              readOnly
              className="w-full h-28 rounded-md bg-zinc-950 border border-zinc-700 p-3 text-sm font-mono"
              value={pack.caption}
            />
            <div className="flex flex-wrap gap-2">
              <button
                type="button"
                onClick={copyCaption}
                className="inline-flex items-center gap-1 px-3 py-2 rounded-md bg-blue-600 text-sm hover:bg-blue-500"
              >
                <Copy className="w-4 h-4" />
                {copied ? "Copied!" : "Copy caption"}
              </button>
              <a
                href={pack.download_url}
                className="inline-flex items-center gap-1 px-3 py-2 rounded-md border border-zinc-700 text-sm hover:bg-zinc-800"
              >
                <Download className="w-4 h-4" />
                Download MP4
              </a>
              <button
                type="button"
                onClick={() => revealMut.mutate()}
                className="inline-flex items-center gap-1 px-3 py-2 rounded-md border border-zinc-700 text-sm hover:bg-zinc-800"
              >
                <FolderOpen className="w-4 h-4" />
                Reveal in Explorer
              </button>
            </div>
            {revealMut.data && (
              <p className="text-xs text-zinc-500">{revealMut.data.message}</p>
            )}
            {pack.output_path && (
              <p className="text-xs text-zinc-600 font-mono break-all">{pack.output_path}</p>
            )}
          </section>

          <section className="rounded-lg border border-zinc-800 bg-zinc-900/80 p-5">
            <h2 className="font-semibold mb-3">Platforms</h2>
            <div className="grid sm:grid-cols-2 gap-3">
              {pack.platforms.map((p) => (
                <div key={p.id} className="border border-zinc-800 rounded-lg p-3">
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-medium text-sm">{p.label}</span>
                    <span className="text-[10px] text-zinc-500">{p.aspect}</span>
                  </div>
                  <p className="text-xs text-zinc-500 mb-2">{p.notes}</p>
                  <a
                    href={p.upload_url}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-1 text-xs text-blue-400 hover:underline"
                  >
                    Open upload <ExternalLink className="w-3 h-3" />
                  </a>
                </div>
              ))}
            </div>
          </section>

          <section className="rounded-lg border border-amber-900/40 bg-amber-950/20 p-4 text-sm text-amber-200/90">
            <h3 className="font-semibold mb-2">Minimum-fuss workflow</h3>
            <ol className="list-decimal list-inside space-y-1 text-amber-200/70">
              {pack.workflow.map((step) => (
                <li key={step}>{step}</li>
              ))}
            </ol>
            <p className="mt-3 text-xs text-zinc-500">
              v0.2: YouTube Data API resumable upload for Shorts. TikTok API needs app review. Postiz for schedule-once.
            </p>
          </section>
        </>
      )}

      {jobId && pack && !pack.ready && (
        <p className="text-sm text-amber-400">Job not complete yet — check Jobs page.</p>
      )}

      {!jobId && (
        <section className="rounded-lg border border-zinc-800 bg-zinc-900/80 p-5 text-sm text-zinc-400">
          <h2 className="font-semibold text-zinc-200 mb-2">Publishing strategy</h2>
          <ul className="space-y-2 list-disc list-inside">
            <li>
              <strong className="text-zinc-300">Tier 1 (now):</strong> This page — download, caption copy, platform deep links.
            </li>
            <li>
              <strong className="text-zinc-300">Tier 2:</strong> YouTube Shorts via Data API (best developer UX).
            </li>
            <li>
              <strong className="text-zinc-300">Tier 3:</strong> TikTok Content Posting API (OAuth + review).
            </li>
            <li>
              <strong className="text-zinc-300">Tier 4:</strong> Self-hosted Postiz to post once to many channels.
            </li>
          </ul>
        </section>
      )}
    </div>
  );
}
