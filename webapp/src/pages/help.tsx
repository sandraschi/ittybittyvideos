import { useState, type ReactNode } from "react";

type HelpTab =
  | "overview"
  | "quickstart"
  | "pipeline"
  | "modes"
  | "footage"
  | "llm"
  | "depot"
  | "publish"
  | "mcp"
  | "troubleshooting";

const TABS: { id: HelpTab; label: string }[] = [
  { id: "overview", label: "Overview" },
  { id: "quickstart", label: "Quick start" },
  { id: "pipeline", label: "Pipeline" },
  { id: "modes", label: "Short vs mid" },
  { id: "footage", label: "Footage" },
  { id: "llm", label: "LLM & settings" },
  { id: "depot", label: "Depot" },
  { id: "publish", label: "Publish" },
  { id: "mcp", label: "MCP & API" },
  { id: "troubleshooting", label: "Troubleshooting" },
];

function Code({ children }: { children: string }) {
  return <code className="text-blue-400 font-mono text-xs">{children}</code>;
}

function Panel({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section className="rounded-lg border border-zinc-800 bg-zinc-900/80 p-5 space-y-3">
      <h2 className="text-lg font-semibold text-zinc-100">{title}</h2>
      <div className="text-zinc-400 space-y-3 leading-relaxed">{children}</div>
    </section>
  );
}

function TabContent({ tab }: { tab: HelpTab }) {
  if (tab === "overview") {
    return (
      <div className="space-y-4">
        <Panel title="What is ittybitty?">
          <p>
            <strong className="text-zinc-200">ittybitty</strong> turns a topic or custom
            narration script into a finished MP4. It is the fleet-grade successor to one-shot
            generators like MoneyPrinterTurbo: tested pipelines, a SQLite <strong>depot</strong>,
            provider plugins, and MCP tools for agents.
          </p>
          <p>
            You can run everything from this dashboard, or drive renders from Claude/Cursor via MCP
            at <Code>/mcp</Code> on port <Code>11054</Code>.
          </p>
        </Panel>
        <Panel title="Main parts">
          <ul className="list-disc list-inside space-y-1">
            <li>
              <strong className="text-zinc-300">Backend</strong> — FastAPI + FastMCP, FFmpeg compose,
              job queue
            </li>
            <li>
              <strong className="text-zinc-300">Webapp</strong> — Generate, Jobs, Depot, Settings,
              Publish, Help (this page)
            </li>
            <li>
              <strong className="text-zinc-300">LocalGen sidecar</strong> — optional Wan 2.2 text-to-video
              on your GPU (port <Code>8188</Code>)
            </li>
            <li>
              <strong className="text-zinc-300">Output</strong> — <Code>./output/</Code> folder plus{" "}
              <Code>depot.db</Code> index
            </li>
          </ul>
        </Panel>
        <Panel title="Typical workflow">
          <ol className="list-decimal list-inside space-y-1">
            <li>Configure API keys in Settings (Pexels + one LLM, or use custom script)</li>
            <li>Generate a short clip from the Generate page</li>
            <li>Track progress on Jobs; finished files land in Depot</li>
            <li>Download or publish manually from Publish</li>
          </ol>
        </Panel>
      </div>
    );
  }

  if (tab === "quickstart") {
    return (
      <div className="space-y-4">
        <Panel title="First run">
          <ol className="list-decimal list-inside space-y-2">
            <li>
              Install FFmpeg and Python 3.10+, then from the repo root:{" "}
              <Code>pip install -e .</Code>
            </li>
            <li>
              Run <Code>start.bat</Code> — starts API on <Code>11054</Code> and Vite on{" "}
              <Code>11055</Code>
            </li>
            <li>
              Open <Code>http://127.0.0.1:11055</Code> for the dev dashboard (hot reload)
            </li>
            <li>
              Single-port UI on <Code>11054</Code> only after <Code>just build-web</Code> (Tauri /
              release)
            </li>
          </ol>
        </Panel>
        <Panel title="Minimum configuration">
          <p>For the default cloud workflow you need:</p>
          <ul className="list-disc list-inside space-y-1">
            <li>
              <Code>PEXELS_API_KEY</Code> — free from pexels.com/api
            </li>
            <li>
              <Code>DEEPSEEK_API_KEY</Code> or <Code>OPENAI_API_KEY</Code> — unless you use{" "}
              <strong className="text-zinc-300">Custom script</strong> mode
            </li>
          </ul>
          <p className="text-zinc-500 text-xs">
            Settings page writes these to <Code>.env</Code>. See repo{" "}
            <Code>docs/CONFIGURATION.md</Code> for every variable.
          </p>
        </Panel>
        <Panel title="Optional: local GPU footage">
          <p>
            On a CUDA machine with ~24 GB VRAM, run <Code>start-localgen.bat</Code>, then set stock
            provider to <strong className="text-zinc-300">localgen</strong> in Settings. No Pexels key
            required for footage (LLM still needed for topic mode).
          </p>
        </Panel>
      </div>
    );
  }

  if (tab === "pipeline") {
    return (
      <div className="space-y-4">
        <Panel title="End-to-end flow">
          <p>Every render follows the same high-level stages:</p>
          <ol className="list-decimal list-inside space-y-2 mt-2">
            <li>
              <strong className="text-zinc-300">Script</strong> — LLM expands a topic into narration
              paragraphs and visual search prompts, or you supply the script directly.
            </li>
            <li>
              <strong className="text-zinc-300">Footage</strong> — For each scene, download Pexels
              clips or generate AI video via LocalGen. Clips are cached under output.
            </li>
            <li>
              <strong className="text-zinc-300">TTS</strong> — Edge TTS (default) reads the narration;
              timing drives subtitles.
            </li>
            <li>
              <strong className="text-zinc-300">Compose</strong> — FFmpeg scales, trims, concatenates
              clips, mixes audio, burns subtitles, writes MP4.
            </li>
            <li>
              <strong className="text-zinc-300">Depot</strong> — Job row updated in SQLite; poster
              frame extracted for the library grid.
            </li>
          </ol>
        </Panel>
        <Panel title="Job states">
          <p>You will see these on the Jobs page and in API status:</p>
          <p className="font-mono text-xs text-zinc-300 mt-2">
            queued → scripting → fetching_footage → tts → composing → completed
          </p>
          <p className="text-zinc-500 text-xs">Failures stop at the stage that errored; check server logs.</p>
        </Panel>
        <Panel title="Provider plugins">
          <p>
            LLM, stock, and TTS backends are separate files under{" "}
            <Code>src/videogen_mcp/providers/</Code>. Adding a provider means registering one module —
            no central router. Active providers appear on Settings and in{" "}
            <Code>videogen_providers</Code> MCP tool.
          </p>
        </Panel>
      </div>
    );
  }

  if (tab === "modes") {
    return (
      <div className="space-y-4">
        <Panel title="Short pipeline (Generate page)">
          <p>
            Target <strong className="text-zinc-300">30–60 seconds</strong>. Best for YouTube Shorts,
            TikTok, Reels. One script block, a handful of B-roll scenes, fast turnaround.
          </p>
          <ul className="list-disc list-inside space-y-1 mt-2">
            <li>Aspect: usually <Code>9:16</Code> vertical; <Code>16:9</Code> supported</li>
            <li>MCP tool: <Code>videogen_generate</Code></li>
            <li>REST: <Code>POST /api/v1/generate</Code></li>
          </ul>
        </Panel>
        <Panel title="Mid-length pipeline">
          <p>
            Target <strong className="text-zinc-300">3–15 minutes</strong>. Uses a planner LLM to
            produce a <strong className="text-zinc-300">chaptered storyboard</strong>, then applies
            videographer rules: hook scene, pacing, B-roll variety, duration rebalancing, transitions.
          </p>
          <ul className="list-disc list-inside space-y-1 mt-2">
            <li>
              Preview plan only: <Code>videogen_plan</Code> / <Code>POST /api/v1/plan</Code>
            </li>
            <li>
              Plan + render: <Code>videogen_plan_render</Code> /{" "}
              <Code>POST /api/v1/plan-render</Code>
            </li>
            <li>More scenes = longer wall time and more API/GPU usage</li>
          </ul>
        </Panel>
        <Panel title="Which should I use?">
          <p>
            Short mode for social clips and experiments. Mid-length when you need explainer or essay
            structure with multiple chapters. Both write to the same Depot.
          </p>
        </Panel>
      </div>
    );
  }

  if (tab === "footage") {
    return (
      <div className="space-y-4">
        <Panel title="Pexels (default)">
          <p>
            Stock provider <Code>pexels</Code> searches royalty-free video for each scene&apos;s keywords.
            Requires <Code>PEXELS_API_KEY</Code>. No GPU. Clips are trimmed to narration length and
            cached so re-runs are cheaper.
          </p>
          <p className="text-zinc-500 text-xs">
            Best general choice: fast, predictable, good for documentary-style B-roll.
          </p>
        </Panel>
        <Panel title="Jellyfin — your library">
          <p>
            Stock provider <Code>jellyfin</Code> searches your Jellyfin server (vacation videos, dog
            cam, phone uploads) and cuts ~5 s segments with ffmpeg. Set{" "}
            <Code>JELLYFIN_SERVER_URL</Code> + <Code>JELLYFIN_API_KEY</Code> — same as{" "}
            <Code>jellyfin-mcp</Code>. Uses direct file paths when the server is local; otherwise
            streams via the Jellyfin API.
          </p>
        </Panel>
        <Panel title="Plex — your library">
          <p>
            Stock provider <Code>plex</Code> works the same way against Plex: search by scene keywords,
            pick in-points deterministically, extract clips. Configure <Code>PLEX_URL</Code> and{" "}
            <Code>PLEX_TOKEN</Code> like <Code>plex-mcp</Code>.
          </p>
        </Panel>
        <Panel title="Google Veo 3.x (cloud)">
          <p>
            Stock provider <Code>veo</Code> generates cinematic AI clips (~5–8 s) via Google&apos;s Veo API.
            Recommended path: run fleet <Code>google-ai-mcp</Code> on port <Code>11014</Code> and set{" "}
            <Code>GOOGLE_AI_MCP_URL</Code> in Settings. Direct mode needs{" "}
            <Code>GOOGLE_CLOUD_PROJECT</Code> and <Code>pip install -e &quot;.[google]&quot;</Code>.
          </p>
        </Panel>
        <Panel title="Gemini Omni Flash (cloud)">
          <p>
            Stock provider <Code>omni</Code> uses multimodal Gemini Omni for text→video (~10 s). Same
            bridge as Veo; useful when you want any-to-any inputs later (image/audio conditioning).
          </p>
        </Panel>
        <Panel title="LocalGen — Wan 2.2 (optional)">
          <p>
            Stock provider <Code>localgen</Code> sends scene prompts to a sidecar on port{" "}
            <Code>8188</Code>. Default backend <Code>wan22-14b</Code> targets RTX 4090-class GPUs;
            use <Code>wan22-5b</Code> if you hit VRAM limits.
          </p>
          <ol className="list-decimal list-inside space-y-1 mt-2">
            <li>
              <Code>pip install -e &quot;.[localgen]&quot;</Code>
            </li>
            <li>
              <Code>start-localgen.bat</Code>
            </li>
            <li>Settings → stock provider → localgen</li>
          </ol>
          <p className="mt-2">
            Legacy name <Code>cogvideo</Code> still maps to the same sidecar; Wan 2.2 replaced
            CogVideoX as the 2026 local default.
          </p>
        </Panel>
        <Panel title="Hybrid (roadmap)">
          <p>
            SPEC R5 plans Pexels-first with AI fallback when search returns weak matches. Today you
            choose one stock provider per job in Settings — not automatic hybrid yet.
          </p>
        </Panel>
      </div>
    );
  }

  if (tab === "llm") {
    return (
      <div className="space-y-4">
        <Panel title="Topic modes">
          <p>The Generate page can call different LLMs to turn a topic into script + search terms:</p>
          <ul className="list-disc list-inside space-y-1 mt-2">
            <li>
              <strong className="text-zinc-300">DeepSeek</strong> — cloud, <Code>DEEPSEEK_API_KEY</Code>
            </li>
            <li>
              <strong className="text-zinc-300">OpenAI</strong> — cloud, <Code>OPENAI_API_KEY</Code>
            </li>
            <li>
              <strong className="text-zinc-300">LM Studio</strong> — local OpenAI-compatible server
            </li>
            <li>
              <strong className="text-zinc-300">Ollama</strong> — local models on port 11434
            </li>
          </ul>
          <p className="mt-2">
            Green indicators on Generate mean that provider passed the Settings health probe.
          </p>
        </Panel>
        <Panel title="Custom script mode">
          <p>
            Paste narration yourself — no LLM call. Footage search terms are still derived from script
            content (or simplified heuristics). Use this when you already have copy or want zero cloud
            LLM cost.
          </p>
        </Panel>
        <Panel title="Settings page">
          <p>
            Edits persist to <Code>.env</Code>. Secret fields are masked on load. Use{" "}
            <strong className="text-zinc-300">Refresh models</strong> for Ollama/LM Studio discovery
            and <strong className="text-zinc-300">Test stock</strong> for Pexels/LocalGen connectivity.
          </p>
        </Panel>
        <Panel title="TTS">
          <p>
            Default <Code>edge-tts</Code> needs no key. Optional <Code>cosyvoice</Code> for local
            Chinese-optimized voices. Subtitles follow TTS timing; install the <Code>align</Code> extra
            for word-level sync.
          </p>
        </Panel>
      </div>
    );
  }

  if (tab === "depot") {
    return (
      <div className="space-y-4">
        <Panel title="What the depot stores">
          <p>
            Every completed (and in-progress) job is tracked in SQLite at{" "}
            <Code>{`{output}/depot.db`}</Code>. The Depot page lists title, duration, aspect, providers
            used, file path, and a poster thumbnail.
          </p>
        </Panel>
        <Panel title="Scan output">
          <p>
            If you copied MP4s into <Code>output/</Code> manually or migrated from an older build,
            click <strong className="text-zinc-300">Scan output</strong> (or{" "}
            <Code>POST /api/v1/depot/scan</Code>) to index files on disk.
          </p>
        </Panel>
        <Panel title="Download & delete">
          <p>
            Download uses safe path resolution — only files under the configured output directory.
            Delete removes the database entry and optionally the video file from disk.
          </p>
        </Panel>
        <Panel title="Jobs page vs Depot">
          <p>
            <strong className="text-zinc-300">Jobs</strong> emphasizes live status for recent renders.{" "}
            <strong className="text-zinc-300">Depot</strong> is your persistent library across restarts.
            Both read the same job store.
          </p>
        </Panel>
      </div>
    );
  }

  if (tab === "publish") {
    return (
      <div className="space-y-4">
        <Panel title="Manual publish (current)">
          <p>
            Fully automated TikTok/YouTube upload needs OAuth and platform app review. Until then,
            ittybitty optimizes for <strong className="text-zinc-300">minimum fuss</strong> manual
            posting:
          </p>
          <ol className="list-decimal list-inside space-y-1 mt-2">
            <li>Generate vertical <Code>9:16</Code> for Shorts / Reels / TikTok</li>
            <li>Download MP4 from Depot or use Reveal in Explorer (Windows)</li>
            <li>Copy suggested caption and <Code>#ittybitty</Code> hashtags from Publish</li>
            <li>Open the platform upload URL in a new browser tab</li>
          </ol>
        </Panel>
        <Panel title="Platform tips">
          <ul className="list-disc list-inside space-y-1">
            <li>YouTube Shorts — under 60 s, vertical, strong first 2 s hook</li>
            <li>TikTok — same aspect; watch safe zones for UI overlays</li>
            <li>Instagram Reels — similar; check audio licensing for stock clips</li>
          </ul>
        </Panel>
        <Panel title="Roadmap">
          <p className="text-zinc-500 text-xs">
            Planned: YouTube Data API one-click Shorts upload; Postiz or similar for multi-platform
            scheduling. See SPEC.md for R-track items.
          </p>
        </Panel>
      </div>
    );
  }

  if (tab === "mcp") {
    return (
      <div className="space-y-4">
        <Panel title="MCP over HTTP">
          <p>
            After starting the server, MCP clients connect to{" "}
            <Code>http://127.0.0.1:11054/mcp</Code> (not stdio). Example Cursor config:
          </p>
          <pre className="mt-2 rounded-md bg-zinc-950 border border-zinc-700 p-3 text-xs text-zinc-300 overflow-x-auto">
            {`{
  "mcpServers": {
    "ittybitty": {
      "url": "http://127.0.0.1:11054/mcp"
    }
  }
}`}
          </pre>
        </Panel>
        <Panel title="Tools">
          <ul className="list-disc list-inside space-y-1 font-mono text-xs text-zinc-300">
            <li>videogen_generate — short render</li>
            <li>videogen_plan — mid storyboard only</li>
            <li>videogen_plan_render — mid full render</li>
            <li>videogen_status — poll job</li>
            <li>videogen_list_jobs — recent jobs</li>
            <li>videogen_providers — list backends</li>
          </ul>
          <p className="text-zinc-500 text-xs mt-2">Full reference: repo docs/TOOLS.md</p>
        </Panel>
        <Panel title="REST & OpenAPI">
          <p>
            Interactive docs at <Code>/docs</Code>. Health check <Code>/health</Code>. Same port as
            the dashboard when using <Code>start.bat</Code>.
          </p>
        </Panel>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <Panel title="Dashboard blank">
        <p>
          Use <Code>http://127.0.0.1:11055</Code> after <Code>start.bat</Code>. If you need the UI
          on <Code>11054</Code>, run <Code>just build-web</Code> then restart the backend.
        </p>
      </Panel>
      <Panel title="Generation errors">
        <ul className="list-disc list-inside space-y-1">
          <li>Pexels — set API key in Settings</li>
          <li>FFmpeg — install and reopen terminal</li>
          <li>LLM — key missing or local server down; try custom script</li>
          <li>LocalGen OOM — switch to wan22-5b or use Pexels</li>
        </ul>
      </Panel>
      <Panel title="More help">
        <p>
          Repo <Code>docs/TROUBLESHOOTING.md</Code>, <Code>INSTALL.md</Code>, and fleet docs at{" "}
          <Code>mcp-central-docs/projects/ittybitty/</Code>.
        </p>
      </Panel>
    </div>
  );
}

export default function Help() {
  const [active, setActive] = useState<HelpTab>("overview");

  return (
    <div className="max-w-4xl space-y-4 text-sm">
      <div>
        <h1 className="text-2xl font-bold text-zinc-100">Help</h1>
        <p className="text-zinc-500 mt-1">
          How ittybitty works — pipeline, providers, depot, and publish.
        </p>
      </div>

      <div
        className="flex gap-1 overflow-x-auto pb-1 border-b border-zinc-800 scrollbar-thin"
        role="tablist"
        aria-label="Help topics"
      >
        {TABS.map(({ id, label }) => {
          const selected = active === id;
          return (
            <button
              key={id}
              type="button"
              role="tab"
              aria-selected={selected}
              onClick={() => setActive(id)}
              className={`shrink-0 rounded-t-md px-3 py-2 text-sm font-medium transition-colors border-b-2 -mb-px ${
                selected
                  ? "border-blue-500 text-blue-400 bg-zinc-900/80"
                  : "border-transparent text-zinc-500 hover:text-zinc-300 hover:bg-zinc-900/40"
              }`}
            >
              {label}
            </button>
          );
        })}
      </div>

      <div role="tabpanel" className="pt-2">
        <TabContent tab={active} />
      </div>
    </div>
  );
}
