import { useQuery } from "@tanstack/react-query";
import { Octagon } from "lucide-react";
import { getStatus } from "@/lib/api";

export default function Topbar() {
  const { data: status } = useQuery({
    queryKey: ["status"],
    queryFn: getStatus,
    refetchInterval: 10000,
  });

  return (
    <header className="h-12 border-b border-zinc-800 bg-zinc-950/80 backdrop-blur flex items-center justify-between px-4 shrink-0">
      <p className="text-sm text-zinc-500">
        Topic in · video out · <span className="text-zinc-300">no degree required</span>
      </p>
      <div className="flex items-center gap-4 text-xs">
        {status && (
          <>
            <span className={status.ffmpeg ? "text-emerald-400" : "text-amber-400"}>
              FFmpeg {status.ffmpeg ? "✓" : "missing"}
            </span>
            <span className="text-zinc-500">v{status.version}</span>
          </>
        )}
        <button
          type="button"
          title="Emergency stop (refresh page; jobs are in-memory)"
          className="flex items-center gap-1 px-2 py-1 rounded bg-red-950/80 text-red-400 border border-red-900 hover:bg-red-900/50"
          onClick={() => window.location.reload()}
        >
          <Octagon className="w-3 h-3" />
          Stop UI
        </button>
      </div>
    </header>
  );
}
