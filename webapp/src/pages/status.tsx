import { useQuery } from "@tanstack/react-query";
import { getHealth, getStatus } from "@/lib/api";

export default function StatusPage() {
  const { data: health } = useQuery({ queryKey: ["health"], queryFn: getHealth, refetchInterval: 5000 });
  const { data: status } = useQuery({ queryKey: ["status"], queryFn: getStatus, refetchInterval: 5000 });

  return (
    <div className="max-w-3xl space-y-4">
      <h1 className="text-2xl font-bold">Status</h1>

      <pre className="rounded-lg border border-zinc-800 bg-zinc-950 p-4 text-xs overflow-x-auto text-zinc-300">
        {JSON.stringify({ health, status }, null, 2)}
      </pre>

      <p className="text-xs text-zinc-500">
        MCP endpoint: <code className="text-blue-400">http://127.0.0.1:11054/mcp</code>
      </p>
    </div>
  );
}
