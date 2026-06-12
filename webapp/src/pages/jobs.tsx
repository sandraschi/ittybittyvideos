import { useSearchParams, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { listJobs } from "@/lib/api";

const statusColor: Record<string, string> = {
  complete: "text-emerald-400",
  failed: "text-red-400",
  pending: "text-zinc-400",
};

export default function Jobs() {
  const [params] = useSearchParams();
  const highlight = params.get("highlight");
  const { data, refetch } = useQuery({
    queryKey: ["jobs"],
    queryFn: () => listJobs(30),
    refetchInterval: (q) => {
      const jobs = q.state.data?.jobs ?? [];
      const busy = jobs.some((j) => !["complete", "failed"].includes(j.status));
      return busy ? 2000 : 10000;
    },
  });

  return (
    <div className="max-w-3xl space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Jobs</h1>
          <p className="text-sm text-zinc-500">
            Live pipeline queue — persisted in depot.db.{" "}
            <Link to="/depot" className="text-blue-400 hover:underline">
              Open Depot
            </Link>{" "}
            for finished videos.
          </p>
        </div>
        <button
          type="button"
          onClick={() => refetch()}
          className="text-xs px-3 py-1.5 rounded border border-zinc-700 hover:bg-zinc-800"
        >
          Refresh
        </button>
      </div>

      <ul className="divide-y divide-zinc-800 rounded-lg border border-zinc-800 bg-zinc-900/80">
        {!data?.jobs?.length && (
          <li className="p-6 text-sm text-zinc-500 text-center">No jobs yet.</li>
        )}
        {data?.jobs.map((j) => (
          <li
            key={j.job_id}
            className={`p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-2 ${
              highlight === j.job_id ? "bg-blue-950/30" : ""
            }`}
          >
            <div className="min-w-0">
              <p className="font-medium truncate">{j.topic || "Untitled"}</p>
              <p className="text-xs text-zinc-500 font-mono">{j.job_id}</p>
            </div>
            <div className="flex items-center gap-3 shrink-0">
              <div className="w-24 h-1.5 bg-zinc-800 rounded overflow-hidden">
                <div
                  className="h-full bg-blue-500 transition-all"
                  style={{ width: `${Math.min(100, j.progress)}%` }}
                />
              </div>
              <span className={`text-xs capitalize w-20 ${statusColor[j.status] ?? "text-amber-400"}`}>
                {j.status}
              </span>
              {j.status === "complete" && (
                <>
                  <Link
                    to={`/publish?job=${j.job_id}`}
                    className="text-xs text-blue-400 hover:underline"
                  >
                    Publish
                  </Link>
                  <Link
                    to="/depot"
                    className="text-xs text-zinc-400 hover:underline"
                  >
                    Depot
                  </Link>
                </>
              )}
            </div>
            {j.error && <p className="text-xs text-red-400 sm:col-span-2">{j.error}</p>}
          </li>
        ))}
      </ul>
    </div>
  );
}
