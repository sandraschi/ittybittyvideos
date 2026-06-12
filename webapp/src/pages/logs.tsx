import { useCallback, useEffect, useRef, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { clearLogs, exportLogsJson, queryLogs, type LogEntry, type LogQueryResult } from "@/lib/api";

const LEVELS = ["", "DEBUG", "INFO", "WARNING", "ERROR"] as const;
const KINDS = ["", "server", "system", "pipeline", "depot", "tool_call"] as const;

function levelClass(level: string): string {
  const l = level.toUpperCase();
  if (l === "ERROR" || l === "CRITICAL") return "text-red-400";
  if (l === "WARNING") return "text-amber-400";
  if (l === "INFO") return "text-sky-400";
  return "text-zinc-500";
}

export default function LogsPage() {
  const [level, setLevel] = useState("");
  const [kind, setKind] = useState("");
  const [search, setSearch] = useState("");
  const [liveTail, setLiveTail] = useState(true);
  const [page, setPage] = useState(0);
  const pageSize = 50;
  const newestIdRef = useRef<string | null>(null);
  const streamRef = useRef<HTMLDivElement>(null);

  const fetchLogs = useCallback(async (): Promise<LogQueryResult> => {
    return queryLogs({
      limit: pageSize,
      offset: page * pageSize,
      level: level || undefined,
      kind: kind || undefined,
      search: search.trim() || undefined,
      sort: "desc",
    });
  }, [page, level, kind, search]);

  const { data, isLoading, refetch, isFetching } = useQuery({
    queryKey: ["logs", page, level, kind, search],
    queryFn: fetchLogs,
    refetchInterval: liveTail && page === 0 ? 2000 : false,
  });

  useEffect(() => {
    if (data?.entries?.[0]?.id) {
      newestIdRef.current = data.entries[0].id;
    }
  }, [data]);

  useEffect(() => {
    if (liveTail && streamRef.current) {
      streamRef.current.scrollTop = 0;
    }
  }, [data, liveTail]);

  async function handleExport() {
    await exportLogsJson({ level: level || undefined, kind: kind || undefined, search: search || undefined });
  }

  async function handleClear() {
    await clearLogs();
    setPage(0);
    await refetch();
  }

  const total = data?.total ?? 0;
  const maxPage = Math.max(0, Math.ceil(total / pageSize) - 1);

  return (
    <div className="max-w-5xl space-y-4 text-sm">
      <div>
        <h1 className="text-2xl font-bold text-zinc-100">Logs</h1>
        <p className="text-zinc-500 mt-1">
          Server, pipeline, and depot events from <code className="text-blue-400">/api/logs</code> ring buffer.
        </p>
      </div>

      <div className="rounded-lg border border-zinc-800 bg-zinc-900/80 p-4 flex flex-wrap gap-3 items-end">
        <label className="block">
          <span className="text-xs text-zinc-500">Level</span>
          <select
            className="mt-1 block rounded-md bg-zinc-950 border border-zinc-700 px-2 py-1.5 text-sm"
            value={level}
            onChange={(e) => {
              setPage(0);
              setLevel(e.target.value);
            }}
          >
            {LEVELS.map((l) => (
              <option key={l || "all"} value={l}>
                {l || "All"}
              </option>
            ))}
          </select>
        </label>
        <label className="block">
          <span className="text-xs text-zinc-500">Kind</span>
          <select
            className="mt-1 block rounded-md bg-zinc-950 border border-zinc-700 px-2 py-1.5 text-sm"
            value={kind}
            onChange={(e) => {
              setPage(0);
              setKind(e.target.value);
            }}
          >
            {KINDS.map((k) => (
              <option key={k || "all"} value={k}>
                {k || "All"}
              </option>
            ))}
          </select>
        </label>
        <label className="block flex-1 min-w-[180px]">
          <span className="text-xs text-zinc-500">Search</span>
          <input
            className="mt-1 w-full rounded-md bg-zinc-950 border border-zinc-700 px-3 py-1.5 text-sm"
            value={search}
            placeholder="Filter detail / meta"
            onChange={(e) => {
              setPage(0);
              setSearch(e.target.value);
            }}
          />
        </label>
        <label className="flex items-center gap-2 text-xs text-zinc-400 pb-1">
          <input
            type="checkbox"
            checked={liveTail}
            onChange={(e) => setLiveTail(e.target.checked)}
            className="rounded border-zinc-600"
          />
          Live tail (2s)
        </label>
        <button
          type="button"
          onClick={() => refetch()}
          className="px-3 py-1.5 rounded-md border border-zinc-700 hover:bg-zinc-800 text-xs"
        >
          {isFetching ? "Refreshing…" : "Refresh"}
        </button>
        <button
          type="button"
          onClick={() => void handleExport()}
          className="px-3 py-1.5 rounded-md border border-zinc-700 hover:bg-zinc-800 text-xs"
        >
          Export JSON
        </button>
        <button
          type="button"
          onClick={() => void handleClear()}
          className="px-3 py-1.5 rounded-md border border-red-900/50 text-red-400 hover:bg-red-950/40 text-xs"
        >
          Clear
        </button>
      </div>

      <div className="flex flex-wrap items-center justify-between gap-2 text-xs text-zinc-500">
        <span>
          {total} entries · max {data?.max_entries ?? 2000}
          {isLoading ? " · loading…" : ""}
        </span>
        <div className="flex items-center gap-2">
          <button
            type="button"
            disabled={page <= 0}
            onClick={() => setPage((p) => Math.max(0, p - 1))}
            className="px-2 py-1 rounded border border-zinc-800 disabled:opacity-40"
          >
            Prev
          </button>
          <span>
            Page {page + 1} / {maxPage + 1}
          </span>
          <button
            type="button"
            disabled={page >= maxPage}
            onClick={() => setPage((p) => p + 1)}
            className="px-2 py-1 rounded border border-zinc-800 disabled:opacity-40"
          >
            Next
          </button>
        </div>
      </div>

      <div
        ref={streamRef}
        className="rounded-lg border border-zinc-800 bg-zinc-950 font-mono text-xs max-h-[65vh] overflow-y-auto"
      >
        {!data?.entries?.length ? (
          <p className="p-4 text-zinc-600">{isLoading ? "Loading…" : "No log entries yet."}</p>
        ) : (
          <table className="w-full text-left">
            <thead className="sticky top-0 bg-zinc-900 text-zinc-500">
              <tr>
                <th className="p-2 w-44">Time</th>
                <th className="p-2 w-20">Level</th>
                <th className="p-2 w-24">Kind</th>
                <th className="p-2">Detail</th>
              </tr>
            </thead>
            <tbody>
              {data.entries.map((e: LogEntry) => (
                <tr key={e.id} className="border-t border-zinc-900/80 hover:bg-zinc-900/50">
                  <td className="p-2 text-zinc-500 whitespace-nowrap">{formatTime(e.timestamp)}</td>
                  <td className={`p-2 ${levelClass(e.level)}`}>{e.level}</td>
                  <td className="p-2 text-zinc-400">{e.kind}</td>
                  <td className="p-2 text-zinc-300 break-all">{e.detail}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

function formatTime(iso: string): string {
  try {
    return new Date(iso).toLocaleString();
  } catch {
    return iso;
  }
}
