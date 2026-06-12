import { useState } from "react";
import { Link } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Download, FolderOpen, RefreshCw, Share2, Trash2 } from "lucide-react";
import { deleteDepotItem, downloadUrl, listDepot, revealJob, scanDepot } from "@/lib/api";

function formatWhen(iso: string) {
  try {
    return new Date(iso).toLocaleString();
  } catch {
    return iso;
  }
}

export default function Depot() {
  const qc = useQueryClient();
  const [confirmId, setConfirmId] = useState<string | null>(null);

  const { data, isLoading, refetch, isFetching } = useQuery({
    queryKey: ["depot"],
    queryFn: () => listDepot(100),
    refetchInterval: 15000,
  });

  const scanMut = useMutation({
    mutationFn: scanDepot,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["depot"] }),
  });

  const deleteMut = useMutation({
    mutationFn: (jobId: string) => deleteDepotItem(jobId, true),
    onSuccess: () => {
      setConfirmId(null);
      qc.invalidateQueries({ queryKey: ["depot"] });
      qc.invalidateQueries({ queryKey: ["jobs"] });
    },
  });

  const revealMut = useMutation({
    mutationFn: (jobId: string) => revealJob(jobId),
  });

  const summary = data?.summary;
  const items = data?.items ?? [];

  return (
    <div className="max-w-6xl space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">Depot</h1>
          <p className="text-sm text-zinc-500 mt-1">
            Persistent library — SQLite + on-disk MP4s survive restarts.
          </p>
          {summary && (
            <p className="text-xs text-zinc-600 mt-2 font-mono break-all">
              {summary.output_dir} · {summary.total} video(s) · {summary.on_disk} on disk
            </p>
          )}
        </div>
        <div className="flex gap-2 shrink-0">
          <button
            type="button"
            onClick={() => refetch()}
            disabled={isFetching}
            className="inline-flex items-center gap-1 text-xs px-3 py-1.5 rounded border border-zinc-700 hover:bg-zinc-800 disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isFetching ? "animate-spin" : ""}`} />
            Refresh
          </button>
          <button
            type="button"
            onClick={() => scanMut.mutate()}
            disabled={scanMut.isPending}
            className="inline-flex items-center gap-1 text-xs px-3 py-1.5 rounded bg-blue-600 hover:bg-blue-500 disabled:opacity-50"
          >
            Scan folder
          </button>
        </div>
      </div>

      {scanMut.data?.message && (
        <p className="text-xs text-emerald-400">{scanMut.data.message}</p>
      )}

      {isLoading && <p className="text-sm text-zinc-500">Loading depot…</p>}

      {!isLoading && items.length === 0 && (
        <div className="rounded-lg border border-zinc-800 bg-zinc-900/80 p-8 text-center text-sm text-zinc-500">
          No videos yet. Generate one, or click <strong className="text-zinc-300">Scan folder</strong> to
          import existing MP4s from the output directory.
        </div>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {items.map((item) => (
          <article
            key={item.job_id}
            className="rounded-lg border border-zinc-800 bg-zinc-900/80 overflow-hidden flex flex-col"
          >
            <div className="aspect-[9/16] max-h-72 bg-black relative">
              {item.has_file ? (
                <video
                  className="w-full h-full object-contain"
                  src={downloadUrl(item.job_id)}
                  poster={item.poster_url || undefined}
                  controls
                  preload="metadata"
                  playsInline
                />
              ) : (
                <div className="flex items-center justify-center h-full text-xs text-zinc-600">Missing file</div>
              )}
              {item.source === "import" && (
                <span className="absolute top-2 left-2 text-[10px] px-1.5 py-0.5 rounded bg-amber-900/80 text-amber-200">
                  imported
                </span>
              )}
            </div>
            <div className="p-3 flex-1 flex flex-col gap-2">
              <div className="min-w-0">
                <p className="font-medium text-sm truncate">{item.topic || "Untitled"}</p>
                <p className="text-[10px] text-zinc-500 font-mono truncate">{item.job_id}</p>
              </div>
              <p className="text-[10px] text-zinc-600">
                {item.file_size_mb > 0 ? `${item.file_size_mb} MB · ` : ""}
                {formatWhen(item.updated_at)}
              </p>
              <div className="flex flex-wrap gap-1.5 mt-auto pt-1">
                {item.has_file && (
                  <>
                    <a
                      href={downloadUrl(item.job_id)}
                      className="inline-flex items-center gap-1 text-[11px] px-2 py-1 rounded border border-zinc-700 hover:bg-zinc-800"
                    >
                      <Download className="w-3 h-3" />
                      MP4
                    </a>
                    <Link
                      to={`/publish?job=${item.job_id}`}
                      className="inline-flex items-center gap-1 text-[11px] px-2 py-1 rounded border border-zinc-700 hover:bg-zinc-800"
                    >
                      <Share2 className="w-3 h-3" />
                      Publish
                    </Link>
                    <button
                      type="button"
                      onClick={() => revealMut.mutate(item.job_id)}
                      className="inline-flex items-center gap-1 text-[11px] px-2 py-1 rounded border border-zinc-700 hover:bg-zinc-800"
                    >
                      <FolderOpen className="w-3 h-3" />
                      Reveal
                    </button>
                  </>
                )}
                {confirmId === item.job_id ? (
                  <>
                    <button
                      type="button"
                      onClick={() => deleteMut.mutate(item.job_id)}
                      disabled={deleteMut.isPending}
                      className="text-[11px] px-2 py-1 rounded bg-red-700 hover:bg-red-600"
                    >
                      Confirm delete
                    </button>
                    <button
                      type="button"
                      onClick={() => setConfirmId(null)}
                      className="text-[11px] px-2 py-1 rounded border border-zinc-700"
                    >
                      Cancel
                    </button>
                  </>
                ) : (
                  <button
                    type="button"
                    onClick={() => setConfirmId(item.job_id)}
                    className="inline-flex items-center gap-1 text-[11px] px-2 py-1 rounded border border-zinc-800 text-zinc-500 hover:text-red-400 hover:border-red-900"
                  >
                    <Trash2 className="w-3 h-3" />
                    Delete
                  </button>
                )}
              </div>
              {revealMut.data?.message && revealMut.variables === item.job_id && (
                <p className="text-[10px] text-zinc-500">{revealMut.data.message}</p>
              )}
            </div>
          </article>
        ))}
      </div>
    </div>
  );
}
