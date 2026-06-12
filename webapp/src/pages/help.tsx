import { useState, type ReactNode } from "react";
import { ExternalHref, HelpLinksCatalog } from "@/components/help/HelpRefPanel";

type HelpTab =
  | "overview"
  | "quickstart"
  | "pipeline"
  | "modes"
  | "features"
  | "footage"
  | "llm"
  | "depot"
  | "publish"
  | "mcp"
  | "links"
  | "troubleshooting";

const TABS: { id: HelpTab; label: string }[] = [
  { id: "overview", label: "Overview" },
  { id: "quickstart", label: "Quick start" },
  { id: "pipeline", label: "Pipeline" },
  { id: "modes", label: "Short vs mid" },
  { id: "features", label: "R1–R3 & talker" },
  { id: "footage", label: "Footage" },
  { id: "llm", label: "LLM & TTS" },
  { id: "depot", label: "Depot" },
  { id: "publish", label: "Publish" },
  { id: "mcp", label: "MCP & API" },
  { id: "links", label: "Links" },
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
            <li>
              Configure API keys in Settings (
              <ExternalHref href="https://www.pexels.com/api/new/">Pexels</ExternalHref> + one LLM, or use
              custom script)
            </li>
            <li>Generate a short clip from the Generate page</li>
            <li>Track progress on Jobs; finished files land in Depot</li>
            <li>Download or publish manually from Publish</li>
          </ol>
        </Panel>
        <Panel title="Documentation in repo">
          <ul className="list-disc list-inside space-y-1 text-xs">
            <li>
              <Code>docs/PROVIDERS-AND-MODELS.md</Code> — registry keys and env vars
            </li>
            <li>
              <Code>docs/EXTERNAL-REFERENCES.md</Code> — official tool homepages (also the Links tab here)
            </li>
            <li>
              <Code>docs/CONFIGURATION.md</Code> — full <Code>.env</Code> reference
            </li>
          </ul>
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
              Install <ExternalHref href="https://ffmpeg.org/download.html">FFmpeg</ExternalHref> and Python
              3.11+, then from the repo root: <Code>pip install -e .</Code>
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
              <Code>PEXELS_API_KEY</Code> — free from{" "}
              <ExternalHref href="https://www.pexels.com/api/new/">pexels.com/api/new</ExternalHref>
            </li>
            <li>
              <Code>DEEPSEEK_API_KEY</Code> (
              <ExternalHref href="https://platform.deepseek.com/">DeepSeek Platform</ExternalHref>) or{" "}
              <Code>OPENAI_API_KEY</Code> (
              <ExternalHref href="https://platform.openai.com/">OpenAI</ExternalHref>) — unless you use{" "}
              <strong className="text-zinc-300">Custom script</strong> mode
            </li>
          </ul>
          <p className="text-zinc-500 text-xs">
            Settings page writes these to <Code>.env</Code>. See{" "}
            <Code>docs/CONFIGURATION.md</Code> for every variable.
          </p>
        </Panel>
        <Panel title="Optional: local GPU footage">
          <p>
            On a CUDA machine with ~24 GB VRAM, run <Code>start-localgen.bat</Code>, then set stock
            provider to <strong className="text-zinc-300">localgen</strong> in Settings (
            <ExternalHref href="https://github.com/Wan-Video/Wan2.2">Wan 2.2</ExternalHref> via
            Diffusers). No Pexels key required for footage (LLM still needed for topic mode).
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
              <strong className="text-zinc-300">Compose</strong> —{" "}
              <ExternalHref href="https://ffmpeg.org/">FFmpeg</ExternalHref> scales, trims, concatenates
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
            <li>MCP tool: <Code>videogen_plan_render</Code> / <Code>POST /api/v1/plan-render</Code></li>
            <li>
              Optional R3 screening passes when a vision LLM is reachable (
              <ExternalHref href="https://docs.ollama.com/api">Ollama</ExternalHref> + VL model)
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

  if (tab === "features") {
    return (
      <div className="space-y-4">
        <Panel title="R1 — Forced alignment & karaoke subtitles">
          <p>
            When TTS does not return word timestamps, ittybitty runs{" "}
            <ExternalHref href="https://github.com/SYSTRAN/faster-whisper">faster-whisper</ExternalHref>{" "}
            to align narration to the audio track. Install: <Code>pip install -e &quot;.[align]&quot;</Code>.
          </p>
          <ul className="list-disc list-inside space-y-1 mt-2 text-xs">
            <li>
              <Code>VIDEOGEN_ALIGN=true</Code> · <Code>VIDEOGEN_SUB_STYLE=karaoke</Code> for highlighted
              ASS
            </li>
            <li>
              <Code>VIDEOGEN_WHISPER_MODEL</Code> (default <Code>small</Code>) ·{" "}
              <Code>VIDEOGEN_WHISPER_DEVICE</Code> auto/cuda/cpu
            </li>
          </ul>
        </Panel>
        <Panel title="R2 — Beat snap & music ducking">
          <p>
            Short pipeline with <Code>bgm_url</Code> can snap scene cuts to beats via{" "}
            <ExternalHref href="https://librosa.org/">librosa</ExternalHref> and duck background music under
            narration with FFmpeg sidechain compression. Install:{" "}
            <Code>pip install -e &quot;.[beats]&quot;</Code>.
          </p>
          <ul className="list-disc list-inside space-y-1 mt-2 text-xs">
            <li>
              <Code>VIDEOGEN_BEAT_SNAP</Code> · <Code>VIDEOGEN_DUCK</Code> ·{" "}
              <Code>VIDEOGEN_BGM_VOLUME</Code>
            </li>
          </ul>
        </Panel>
        <Panel title="R3 — Screening Room (VLM self-critique)">
          <p>
            After mid-length render (or via MCP <Code>videogen_review</Code>), sample frames are sent to an
            OpenAI-compatible vision endpoint — typically{" "}
            <ExternalHref href="https://ollama.com/">Ollama</ExternalHref> with a VL model such as{" "}
            <ExternalHref href="https://github.com/QwenLM/Qwen-VL">Qwen-VL</ExternalHref>.
          </p>
          <ul className="list-disc list-inside space-y-1 mt-2 text-xs">
            <li>
              <Code>VIDEOGEN_VLM_URL</Code> (default <Code>http://localhost:11434/v1</Code>)
            </li>
            <li>
              <Code>VIDEOGEN_VLM_MODEL</Code> · <Code>VIDEOGEN_SCREENING_PASSES</Code>
            </li>
            <li>Outputs <Code>critique_pass_*.json</Code> in the job work directory</li>
          </ul>
        </Panel>
        <Panel title="R9 — Talking-head PiP overlay">
          <p>
            Optional post-pass on <strong className="text-zinc-300">short</strong> renders. Requires a source
            face image and an external HTTP service — not bundled. Default contract:{" "}
            <Code>{"POST {TALKER_URL}/generate"}</Code> with <Code>audio</Code> + <Code>image</Code> → MP4.
          </p>
          <p className="mt-2">
            Compatible upstream projects:{" "}
            <ExternalHref href="https://github.com/OpenTalker/SadTalker">SadTalker</ExternalHref>,{" "}
            <ExternalHref href="https://github.com/KlingTeam/LivePortrait">LivePortrait</ExternalHref>,{" "}
            <ExternalHref href="https://github.com/antgroup/echomimic">EchoMimic</ExternalHref>.
          </p>
          <ul className="list-disc list-inside space-y-1 mt-2 text-xs">
            <li>
              <Code>VIDEOGEN_TALKER_PROVIDER=sadtalker</Code> · <Code>TALKER_URL</Code> (default{" "}
              <Code>:11100</Code>)
            </li>
            <li>
              <Code>VIDEOGEN_TALKER_SOURCE</Code> — path to PNG/JPG (human, anime, or pet portrait)
            </li>
          </ul>
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
            Requires <Code>PEXELS_API_KEY</Code> from{" "}
            <ExternalHref href="https://www.pexels.com/api/new/">Pexels API</ExternalHref> (
            <ExternalHref href="https://www.pexels.com/api/documentation/">docs</ExternalHref>). No GPU. Clips
            are trimmed to narration length and cached so re-runs are cheaper.
          </p>
          <p className="text-zinc-500 text-xs">
            Best general choice: fast, predictable, good for documentary-style B-roll.
          </p>
        </Panel>
        <Panel title="Jellyfin — your library">
          <p>
            Stock provider <Code>jellyfin</Code> searches your{" "}
            <ExternalHref href="https://jellyfin.org/">Jellyfin</ExternalHref> server (vacation videos, dog
            cam, phone uploads) and cuts ~5 s segments with ffmpeg. Set <Code>JELLYFIN_SERVER_URL</Code> +{" "}
            <Code>JELLYFIN_API_KEY</Code> — same as fleet <Code>jellyfin-mcp</Code>. API reference:{" "}
            <ExternalHref href="https://api.jellyfin.org/">api.jellyfin.org</ExternalHref>.
          </p>
        </Panel>
        <Panel title="Plex — your library">
          <p>
            Stock provider <Code>plex</Code> works the same way against{" "}
            <ExternalHref href="https://www.plex.tv/">Plex</ExternalHref>: search by scene keywords, pick
            in-points deterministically, extract clips. Configure <Code>PLEX_URL</Code> and{" "}
            <Code>PLEX_TOKEN</Code> like <Code>plex-mcp</Code> (
            <ExternalHref href="https://developer.plex.tv/">Plex developer docs</ExternalHref>).
          </p>
        </Panel>
        <Panel title="Google Veo 3.x (cloud)">
          <p>
            Stock provider <Code>veo</Code> generates cinematic AI clips (~5–8 s) via Google&apos;s Veo API (
            <ExternalHref href="https://ai.google.dev/gemini-api/docs/video">Gemini API video docs</ExternalHref>
            ). Recommended path: run fleet <Code>google-ai-mcp</Code> (
            <ExternalHref href="https://github.com/sandraschi/google-ai-mcp">GitHub</ExternalHref>) on port{" "}
            <Code>11014</Code> and set <Code>GOOGLE_AI_MCP_URL</Code> in Settings. Direct mode needs{" "}
            <Code>GOOGLE_CLOUD_PROJECT</Code> and{" "}
            <ExternalHref href="https://cloud.google.com/vertex-ai/generative-ai/docs/video/generate-videos-from-text">
              Vertex AI video generation
            </ExternalHref>
            .
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
            <Code>8188</Code>. Backend{" "}
            <ExternalHref href="https://github.com/Wan-Video/Wan2.2">Wan 2.2</ExternalHref> via{" "}
            <ExternalHref href="https://huggingface.co/docs/diffusers">Diffusers</ExternalHref>; default{" "}
            <Code>wan22-14b</Code> targets RTX 4090-class GPUs; use <Code>wan22-5b</Code> if you hit VRAM
            limits.
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
        <Panel title="Fleet local generators (externals)">
          <p>
            Sandra&apos;s fleet keeps heavier native stacks beside the repo. They are{" "}
            <strong className="text-zinc-300">not</strong> auto-started by ittybitty — see{" "}
            <Code>docs/LOCAL-VIDEO-GENERATORS.md</Code>.
          </p>
          <ul className="list-disc list-inside space-y-2 mt-2 text-sm">
            <li>
              <strong className="text-zinc-300">wan-video</strong> —{" "}
              <Code>D:\Dev\repos\externals\wan-video</Code> · full{" "}
              <ExternalHref href="https://github.com/Wan-Video/Wan2.2">Wan 2.2</ExternalHref> CLI/MCP
              (S2V, Animate). Same model family as LocalGen; future: HTTP wrapper for{" "}
              <Code>LOCALGEN_URL</Code>.
            </li>
            <li>
              <strong className="text-zinc-300">hunyuan-worldplay</strong> —{" "}
              <Code>D:\Dev\repos\externals\hunyuan-worldplay</Code> ·{" "}
              <ExternalHref href="https://3d-models.hunyuan.tencent.com/world/">HY-World 1.5</ExternalHref>{" "}
              interactive streaming worlds (roadmap stock provider).
            </li>
          </ul>
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
              <strong className="text-zinc-300">DeepSeek</strong> —{" "}
              <ExternalHref href="https://platform.deepseek.com/">platform.deepseek.com</ExternalHref>
            </li>
            <li>
              <strong className="text-zinc-300">OpenAI</strong> —{" "}
              <ExternalHref href="https://platform.openai.com/">platform.openai.com</ExternalHref>
            </li>
            <li>
              <strong className="text-zinc-300">LM Studio</strong> —{" "}
              <ExternalHref href="https://lmstudio.ai/">local OpenAI-compatible server</ExternalHref>
            </li>
            <li>
              <strong className="text-zinc-300">Ollama</strong> —{" "}
              <ExternalHref href="https://ollama.com/">ollama.com</ExternalHref> (
              <ExternalHref href="https://docs.ollama.com/api">API</ExternalHref>)
            </li>
            <li>
              <strong className="text-zinc-300">Qwen</strong> —{" "}
              <ExternalHref href="https://help.aliyun.com/zh/dashscope/">DashScope</ExternalHref>
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
            Default <Code>edge-tts</Code> (
            <ExternalHref href="https://github.com/rany2/edge-tts">rany2/edge-tts</ExternalHref>) uses
            Microsoft Edge online voices — no API key. Optional <Code>cosyvoice</Code> (
            <ExternalHref href="https://github.com/FunAudioLLM/CosyVoice">FunAudioLLM/CosyVoice</ExternalHref>
            ) for local zero-shot voices. Subtitles follow TTS timing; install the <Code>align</Code> extra
            for word-level sync and karaoke ASS.
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
            <li>videogen_plan_render — mid full render (+ optional R3 screening)</li>
            <li>videogen_status — poll job</li>
            <li>videogen_list_jobs — recent jobs</li>
            <li>videogen_providers — list backends (LLM, stock, TTS, talker)</li>
            <li>videogen_review — R3 VLM critique of finished MP4</li>
          </ul>
          <p className="text-zinc-500 text-xs mt-2">
            Full reference: <Code>docs/TOOLS.md</Code> ·{" "}
            <ExternalHref href="https://gofastmcp.com/">FastMCP</ExternalHref> HTTP transport
          </p>
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

  if (tab === "links") {
    return <HelpLinksCatalog />;
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
          <li>
            Pexels — set API key in Settings (
            <ExternalHref href="https://www.pexels.com/api/new/">get key</ExternalHref>)
          </li>
          <li>
            FFmpeg — install from{" "}
            <ExternalHref href="https://ffmpeg.org/download.html">ffmpeg.org</ExternalHref> and reopen
            terminal
          </li>
          <li>LLM — key missing or local server down; try custom script or check Ollama/LM Studio</li>
          <li>LocalGen OOM — switch to wan22-5b or use Pexels</li>
          <li>R3 screening skipped — start Ollama with a vision model; see Features tab</li>
          <li>R9 talker skipped — external SadTalker/LivePortrait service on TALKER_URL</li>
        </ul>
      </Panel>
      <Panel title="More help">
        <p>
          Repo <Code>docs/TROUBLESHOOTING.md</Code>, <Code>docs/EXTERNAL-REFERENCES.md</Code>,{" "}
          <Code>INSTALL.md</Code>, and fleet docs at <Code>mcp-central-docs/projects/ittybitty/</Code>.
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
          Pipeline, providers, depot, publish — plus official tool links.
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
