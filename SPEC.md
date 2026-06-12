# videogen-mcp ("roughcut") — AI Video Generation MCP Server

**Version**: 0.1.0
**Port**: 11054 (backend, serves webapp dist) / 11055 (Vite dev server)
**Status**: MVP — core pipeline + mid-length mode; SOTA webapp (React/Vite, 10 pages)

**Fleet docs:** [ASSESSMENT-BY-CURSOR.md](./ASSESSMENT-BY-CURSOR.md) · [MCD project page](../mcp-central-docs/projects/roughcut/README.md) · [Competition analysis](../mcp-central-docs/projects/roughcut/COMPETITIVE_ANALYSIS.md)

## Problem

MoneyPrinterTurbo proved the market (86k stars): topic in → short video out.
But it ships with zero tests, a monolith LLM router, bundled proprietary fonts,
TOML-only config, no mid-length support, and no MCP integration. We build the
fleet-grade version.

## Architecture

```
Topic/Keyword
     │
     ▼
┌──────────────────────────────────────────────────────┐
│  videogen-mcp (FastMCP 3.2 + FastAPI, port 11054)    │
│                                                       │
│  Short pipeline (30-60s):                             │
│  1. LLM Provider → script + search terms              │
│  2. Stock Provider → footage clips (cached)           │
│  3. TTS Provider → narration audio + subtitles        │
│  4. Compose Service → FFmpeg → final .mp4             │
│                                                       │
│  Mid-length pipeline (3-15 min):                      │
│  1. Planner (LLM) → chaptered storyboard              │
│  2. Videographer rules → hook, pacing, B-roll,        │
│     transitions, duration rebalancing                 │
│  3. Scene-by-scene footage + TTS + subtitles          │
│  4. FFmpeg compose with chapter structure             │
│                                                       │
│  Plugin Registry (implemented):                       │
│  ├── LLM:   openai, ollama, qwen                      │
│  ├── Stock: pexels, cogvideo                          │
│  └── TTS:   edge-tts, cosyvoice                       │
└──────────────────────────────────────────────────────┘
```

MCP is mounted at `/mcp` on the same FastAPI app (`mcp.http_app()`); FastMCP
import is optional — REST API works standalone if fastmcp is absent.

## Provider Plugin System

Each provider is one file registering via decorator (`@register_llm("qwen")`
etc.) against a base class in `providers/base.py`. Adding a provider = adding
one file. No monolith router.

### Chinese Open-Weight Stack

Fully local operation on GPU, no cloud keys required:

| Provider | Model | Local backend | Cloud fallback |
|----------|-------|---------------|----------------|
| `qwen` | Qwen 3 | Ollama (`qwen3:8b`, port 11434) | DashScope (`DASHSCOPE_API_KEY`) |
| `cosyvoice` | CosyVoice 2 | CosyVoice server (port 9880) | DashScope |
| `cogvideo` | CogVideoX | ComfyUI / inference server (port 8188) | ZhipuAI |

**Known limitation (resolved by R1)**: without the `align` extra installed,
CosyVoice subtitles fall back to sentence-level estimated timestamps
(duration heuristic: CJK chars × 0.35s + latin words × 0.4s). With
`uv sync --extra align`, faster-whisper alignment provides word-level
timing for every provider.

## MCP Tools (implemented)

| Tool | Description |
|------|-------------|
| `videogen_generate` | Short video (30-60s) from topic or custom script |
| `videogen_plan` | Plan mid-length chaptered storyboard (preview, no render) |
| `videogen_plan_render` | Plan AND render mid-length video (3-15 min) |
| `videogen_status` | Poll job progress |
| `videogen_list_jobs` | List recent jobs (limit 1-50) |
| `videogen_providers` | List available LLM/stock/TTS providers |

## REST API

| Endpoint | Method |
|----------|--------|
| `/health` | GET |
| `/api/v1/generate` | POST |
| `/api/v1/plan` | POST |
| `/api/v1/plan/render` | POST |
| `/api/v1/jobs` | GET |
| `/api/v1/jobs/{id}` | GET |
| `/api/v1/jobs/{id}/download` | GET |
| `/api/v1/providers` | GET |
| `/api/v1/jobs/{id}/publish-pack` | GET |
| `/api/v1/jobs/{id}/reveal` | POST |
| `/api/v1/status` | GET |
| `/api/v1/tools` | GET |
| `/` + `/assets` | webapp dist (after `just build-web`) |

## Config

12-factor env vars with `.env` support (pydantic-settings, `extra="ignore"`).

Core (`config/settings.py`):
- `VIDEOGEN_LLM_PROVIDER` (default: openai)
- `VIDEOGEN_STOCK_PROVIDER` (default: pexels)
- `VIDEOGEN_TTS_PROVIDER` (default: edge-tts)
- `OPENAI_API_KEY`, `OPENAI_BASE_URL`, `OPENAI_MODEL` (default: gpt-4o-mini)
- `PEXELS_API_KEY`
- `EDGE_TTS_VOICE` (default: en-US-AriaNeural)
- `VIDEOGEN_OUTPUT_DIR` (./output), `VIDEOGEN_CACHE_DIR` (./cache)
- `VIDEOGEN_HOST` (127.0.0.1), `VIDEOGEN_PORT` (11054)
- `VIDEOGEN_DEFAULT_ASPECT` (9:16), `VIDEOGEN_DEFAULT_FPS` (30)
- `VIDEOGEN_CLIP_DURATION` (5.0), `VIDEOGEN_PARAGRAPH_COUNT` (3)

Provider-local (read via os.environ, not in Settings):
- `DASHSCOPE_API_KEY`, `QWEN_MODEL` (qwen-plus cloud / qwen3:8b local)
- `COSYVOICE_URL` (default: http://localhost:9880)
- `COGVIDEO_URL` (default: http://localhost:8188)

## Native Packaging

`native/` contains a Tauri shell ("roughcut") wrapping a PyInstaller-built
backend (`roughcut-backend.exe`, spec at repo root). NSIS hooks in
`native/windows/`. Build via `native/build.ps1`.

## Roadmap (v0.2 — v0.5)

Sequenced by leverage-per-effort. AI-assisted timelines.

### Phase 1 — Audio honesty (v0.2, ~2 days)

**R1. Forced alignment for word-level subtitles (all TTS providers) — DONE 2026-06-12**
Run faster-whisper alignment on the *generated* narration audio, regardless
of provider. Replaces CosyVoice's duration heuristic and any provider-specific
timestamp plumbing with one universal post-pass.
- New: `services/align.py` — `align(audio_path, text) -> list[WordTimestamp]`
- Dep: `faster-whisper` (CTranslate2, runs on RTX 4090 or CPU)
- Subtitle service gains karaoke mode: word-highlight ASS styling (the
  caption style that performs on shorts), toggle `VIDEOGEN_SUB_STYLE=karaoke|sentence`
- Acceptance: CosyVoice job produces word-level .ass; sub timing within ±150ms
  of audio on test fixture. Removes the README roadmap caveat.

**R2. Beat-aware cuts + music ducking**
- `services/audio.py`: librosa beat-grid on the background track; compose
  service snaps scene cut points to nearest beat (tolerance ±400ms, never
  violates videographer pacing clamps).
- FFmpeg `sidechaincompress` ducks music under narration (no manual keyframes).
- Dep: `librosa`. Env: `VIDEOGEN_BEAT_SNAP=true`, `VIDEOGEN_DUCK_DB=-12`
- Acceptance: golden test asserts cut timestamps land on detected beats;
  ducked stem RMS under narration ≥10dB below music-only segments.

### Phase 2 — The star-makers (v0.3, ~4-5 days)

**R3. Screening Room — closed-loop self-critique**
Render draft at 480p → extract one frame per scene → local VLM
(Qwen3.5-VL via Ollama/LM Studio) reviews frames + narration + subtitle
boxes like an editor watching dailies. Structured critique JSON:
`{scene_id, verdict, issues: [footage_mismatch|pacing|sub_collision|weak_hook], fix_hint}`.
Planner re-plans only flagged scenes; re-render; max N passes.
- New: `services/critic.py`, `videogen_review` MCP tool (review existing job),
  `--screening-passes` on plan_render (default 1, 0 = off)
- Env: `VIDEOGEN_VLM_URL`, `VIDEOGEN_VLM_MODEL` (default qwen3.5-vl via Ollama)
- Headline feature: nobody in the MPT-clone genre does closed-loop QC.
- Acceptance: fixture with deliberately mismatched clip gets flagged and
  replaced; pass count and critique log stored on the job record.

**R4. Source-grounded mode (paper/URL/repo → video)**
`videogen_plan(source_url=...)`: fetch + chunk source (arXiv HTML→markdown
path exists in arxiv-mcp; generalize a minimal fetcher here), script generation
grounded in chunks, citations rendered as lower-thirds with source + section.
- New: `services/grounding.py`, `models/citation.py`; lower-third renderer
  in compose (ASS overlay track)
- Tools: `source_url` param on plan/plan_render; REST passthrough
- Demo target: arXiv paper → 5-min explainer, fully local. This is the
  Show HN video.
- Acceptance: every script chapter carries ≥1 citation to a real chunk;
  hallucinated-citation test (chunk text scrambled → planner must abstain).

### Phase 3 — From generator to tool (v0.4, ~4 days)

**R5. Semantic footage matching**
Embed scene narration + Pexels metadata (title/tags) with a local embedding
model; select clips by cosine similarity, not keyword roulette. Constraints:
no clip reuse within a video, alternate wide/close where metadata allows.
- New: `services/matcher.py`. Dep: `sentence-transformers` (bge-small or
  similar, CPU-fine). Env: `VIDEOGEN_MATCH_THRESHOLD=0.35` (below → fall
  back to cogvideo generation if enabled)
- Acceptance: eval set of 20 narration lines: top-1 clip relevance (human-
  labeled) ≥80%, vs ~50% keyword baseline.

**R6. Scene-level content-addressed cache + storyboard editor webapp**
Cache key = hash(scene script, voice, clip id, aspect, style). Editing one
scene re-renders one scene. Webapp (`webapp/src`, currently empty) becomes
a storyboard editor: scene cards with thumbnails, drag to reorder, inline
narration edit, clip swap from match candidates, render button, SSE progress
per scene.
- Backend: `services/scene_cache.py`; `PATCH /api/v1/jobs/{id}/scenes/{n}`;
  SSE at `/api/v1/jobs/{id}/events`
- Frontend: Vite/React per WEBAPP_SOTA_STANDARDS, Bun, port 11055;
  Playwright e2e headless in `webapp/e2e`
- Acceptance: single-scene narration edit re-renders in <30s on Goliath;
  full re-render untouched scenes = 100% cache hits.

### Phase 4 — Community + fleet (v0.5, ~2 days)

**R7. Templates as data**
`templates/*.json` style presets: fonts, color grade (FFmpeg LUT/eq), 
transition pack, music genre tags, pacing profile. Ship 4-5 presets
(e.g. "documentary", "tutorial-clean", "hype-short", "lo-fi"). 
`videogen_templates` tool returns from Planned (list/apply).
Contribution surface: "add a template" = perfect first PR.
- Acceptance: same topic rendered with two templates produces visibly
  distinct font/grade/transitions; template schema validated in tests.

**R8. Fleet bridge — morning briefing**
aiwatcher digest → videogen plan_render → output dir watched by Plex.
Thin glue: `scripts/morning_briefing.py` + scheduled task; aiwatcher's
`generate_digest` output as grounded source (reuses R4).
- Acceptance: end-to-end run produces a 3-min narrated news video from
  yesterday's top-scored items. README GIF candidate.

### Deferred

- LLM providers: gemini, deepseek (40-line plugin each, on demand)
- Stock: pixabay, veo bridge; TTS: speech-mcp bridge
- mcpb packaging; VRM avatar presenter overlay (vroidstudio-mcp, stretch)

## Testing

42 tests (`just test`), ruff (`just lint`), pyright basic (`just typecheck`),
`just check` for all three. Test coverage: cache, compose, providers, schema,
server, storyboard, videographer.
