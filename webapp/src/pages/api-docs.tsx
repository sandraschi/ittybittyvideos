import { useState } from "react";
import { ExternalLink } from "lucide-react";

export default function ApiDocs() {
  const [view, setView] = useState<"swagger" | "redoc">("swagger");
  const backend = "http://127.0.0.1:11054";

  const endpoints = [
    "GET /health",
    "GET /api/v1/status",
    "POST /api/v1/generate",
    "POST /api/v1/plan",
    "POST /api/v1/plan/render",
    "GET /api/v1/jobs",
    "GET /api/v1/jobs/{id}/publish-pack",
    "POST /api/v1/jobs/{id}/reveal",
  ];

  return (
    <div className="max-w-5xl space-y-4 h-[calc(100vh-6rem)] flex flex-col">
      <div className="flex items-center justify-between shrink-0">
        <div>
          <h1 className="text-2xl font-bold">API Docs</h1>
          <p className="text-sm text-zinc-500">FastAPI OpenAPI · proxied in dev</p>
        </div>
        <div className="flex gap-2 items-center">
          <button
            type="button"
            onClick={() => setView("swagger")}
            className={`text-xs px-2 py-1 rounded ${view === "swagger" ? "bg-blue-600" : "bg-zinc-800"}`}
          >
            Swagger
          </button>
          <button
            type="button"
            onClick={() => setView("redoc")}
            className={`text-xs px-2 py-1 rounded ${view === "redoc" ? "bg-blue-600" : "bg-zinc-800"}`}
          >
            ReDoc
          </button>
          <a
            href={`${backend}/docs`}
            target="_blank"
            rel="noreferrer"
            className="text-xs text-blue-400 inline-flex items-center gap-1"
          >
            Open in browser <ExternalLink className="w-3 h-3" />
          </a>
        </div>
      </div>

      <div className="flex flex-wrap gap-2 text-[10px] font-mono text-zinc-500 shrink-0">
        {endpoints.map((e) => (
          <span key={e} className="px-2 py-1 rounded bg-zinc-900 border border-zinc-800">
            {e}
          </span>
        ))}
      </div>

      <iframe
        title="API documentation"
        className="flex-1 w-full rounded-lg border border-zinc-800 bg-zinc-950 min-h-[400px]"
        src={view === "swagger" ? "/docs" : "/redoc"}
      />
    </div>
  );
}
