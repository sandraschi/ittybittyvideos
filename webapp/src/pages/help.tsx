export default function Help() {
  return (
    <div className="max-w-3xl space-y-6 text-sm">
      <h1 className="text-2xl font-bold">Help</h1>

      <section className="rounded-lg border border-zinc-800 bg-zinc-900/80 p-5 space-y-2">
        <h2 className="text-lg font-semibold">Getting started</h2>
        <ol className="list-decimal list-inside text-zinc-400 space-y-1">
          <li>Copy <code className="text-blue-400">.env.example</code> → <code className="text-blue-400">.env</code></li>
          <li>Set <code className="text-blue-400">OPENAI_API_KEY</code> and <code className="text-blue-400">PEXELS_API_KEY</code></li>
          <li>Install FFmpeg on PATH</li>
          <li>Run <code className="text-blue-400">webapp/start.ps1</code> or <code className="text-blue-400">just web</code></li>
          <li>Open <code className="text-blue-400">http://127.0.0.1:11055</code></li>
        </ol>
      </section>

      <section className="rounded-lg border border-zinc-800 bg-zinc-900/80 p-5 space-y-2">
        <h2 className="text-lg font-semibold">Publishing (minimum fuss)</h2>
        <p className="text-zinc-400">
          Automated posting to TikTok/Reels requires OAuth and app review. Until then, use the{" "}
          <strong className="text-zinc-200">Publish</strong> page:
        </p>
        <ul className="list-disc list-inside text-zinc-400 space-y-1">
          <li>Generate vertical 9:16 for TikTok / Reels / Douyin</li>
          <li>Download MP4 or Reveal in Explorer (Windows)</li>
          <li>Copy caption + hashtags</li>
          <li>Open platform upload URL in new tab</li>
        </ul>
        <p className="text-zinc-500 text-xs mt-2">
          Next: YouTube Data API for one-click Shorts upload. Postiz for multi-platform scheduling.
        </p>
      </section>

      <section className="rounded-lg border border-zinc-800 bg-zinc-900/80 p-5">
        <h2 className="text-lg font-semibold mb-2">Fleet docs</h2>
        <ul className="text-zinc-400 space-y-1">
          <li>
            MCD:{" "}
            <code className="text-blue-400">mcp-central-docs/projects/roughcut/README.md</code>
          </li>
          <li>
            Assessment: <code className="text-blue-400">ASSESSMENT-BY-CURSOR.md</code>
          </li>
          <li>
            Competition: <code className="text-blue-400">projects/roughcut/COMPETITIVE_ANALYSIS.md</code>
          </li>
        </ul>
      </section>
    </div>
  );
}
