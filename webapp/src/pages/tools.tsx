import { useQuery } from "@tanstack/react-query";
import { getTools } from "@/lib/api";

export default function Tools() {
  const { data, isLoading } = useQuery({ queryKey: ["tools"], queryFn: getTools });

  return (
    <div className="max-w-3xl space-y-4">
      <div>
        <h1 className="text-2xl font-bold">Tools</h1>
        <p className="text-sm text-zinc-500 mt-1">MCP tools exposed at <code className="text-blue-400">/mcp</code></p>
      </div>

      {isLoading && <p className="text-sm text-zinc-500">Loading…</p>}

      <div className="grid gap-3">
        {data?.tools.map((t) => (
          <div key={t.name} className="rounded-lg border border-zinc-800 bg-zinc-900/80 p-4">
            <div className="flex items-center gap-2 mb-1">
              <code className="text-blue-400 text-sm">{t.name}</code>
              <span className="text-[10px] uppercase px-1.5 py-0.5 rounded bg-zinc-800 text-zinc-500">{t.kind}</span>
            </div>
            <p className="text-sm text-zinc-400">{t.description}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
