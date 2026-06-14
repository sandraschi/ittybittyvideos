# ittybittyvideos -- Technical Assessment

**Author**: Sandra Schipal (Vienna)
**Date**: 2026-06-13
**Repo**: https://github.com/sandraschi/ittybittyvideos
**Version**: 0.2.0+
**Tests**: 193+ passing | **Lint**: clean | **Port**: 11054

---

## Origin

Built in one afternoon as a fleet-grade response to MoneyPrinterTurbo (86k stars, zero tests). Scaffolded by opencode (deepseek-v4-pro), extended by Cursor, debugged and released same day.

## Architecture

Plugin provider system -- each provider is one file with one decorator. Adding a provider never touches existing code. The monolith LLM router problem (MPT's 2000-line single file for 17 providers) is solved at the architecture level.

```
Topic --> Trope Director --> LLM Storyboard --> Videographer Rules
  --> Stock Footage / AI Video --> TTS + Whisper Alignment
  --> Beat-snap + Ducking --> FFmpeg Compose --> Screening Room
  --> .mp4
```

## Test Coverage

| Layer | Tests | What's Covered |
|-------|-------|----------------|
| Schema / models | 13 | Pydantic models, enums, defaults |
| Providers | 15 | Registration, resolution, parsing, health |
| LLM resolver | 8 | Auto-detection, fallback chain, setup hints |
| Cache | 3 | Determinism, dedup, miss handling |
| Compose | 6 | SRT generation, time formatting |
| Storyboard | 6 | Scenes, chapters, duration, plan requests |
| Videographer | 8 | Hook, outro, pacing, B-roll, transitions, rebalancing |
| Server / REST | 10 | Health, jobs, depot, settings, providers, tools |
| Job store | 7 | SQLite persistence, orphan scan, depot |
| Config store | 3 | .env mutation, reload, secret preservation |
| Alignment | 17 | Whisper words, ASS karaoke, sentence breaking, CJK |
| Google video | 5 | Veo/Omni registration, URL parsing, status |
| Library stock | 5 | Jellyfin/Plex registration, clip picking, mock search |
| LocalGen | 3 | Health, missing deps, mock generation |
| Logs API | 3 | Activity logging, filtering, route mounting |
| Publish | 3 | Platform listing, pack generation |
| Visual look | 4 | AI provider detection, suffix application |
| Webapp | 2 | Repo root, dist detection |
| Stock status | 2 | Provider probing |
| **Total** | **181** | |

## Provider Inventory (12 plugins)

### LLM (5)
- `openai` -- OpenAI API (any compatible endpoint)
- `ollama` -- Local Ollama (llama3, qwen3, etc.)
- `qwen` -- Alibaba DashScope cloud or local Ollama qwen3:8b
- `deepseek` -- DeepSeek API
- `lmstudio` -- LM Studio local server

### Stock Footage (9 registry keys)
- `pexels` -- Pexels video API (free tier)
- `pixabay` -- Pixabay video API (free tier)
- `coverr` -- Coverr video API (free tier)
- `localgen` / `cogvideo` -- Local AI video (Wan 2.2 sidecar)
- `veo` / `omni` -- Google cloud AI footage
- `jellyfin` / `plex` -- Home library B-roll

### TTS (2)
- `edge-tts` -- Microsoft Edge TTS (free, no API key)
- `cosyvoice` -- Alibaba CosyVoice 2 (local GPU, voice cloning)

## Key Differentiators vs MoneyPrinterTurbo

| Capability | MPT | ittybittyvideos |
|-----------|-----|-----------------|
| Tests | 0 | 193+ |
| Max video length | ~60s | 15 min (chaptered storyboard) |
| Scene planning | None | LLM storyboard + videographer rules engine |
| Creative direction | Raw LLM prompt | Trope director + viral pattern library + intro contrast packs |
| Self-review | None | VLM screening room (AI watches and critiques its own output) |
| Subtitle precision | Edge TTS timestamps | faster-whisper forced alignment + karaoke ASS |
| Audio editing | None | Beat-snap cuts + ducking |
| Stock sources | 3 free APIs (Pexels, Pixabay, Coverr) | Same 3 **+ Veo, Omni, LocalGen, Jellyfin/Plex** |
| LLM architecture | 2000-line monolith router | Plugin registry + auto-resolver |
| Config | TOML file, secrets in plaintext | 12-factor env vars, runtime .env mutation from UI |
| Persistence | None (in-memory) | SQLite job store, depot, config store |
| Desktop app | None | Tauri 2.0 NSIS installer (31 MB) |
| Webapp | Streamlit | React + Vite (10+ pages) |
| CI/CD | None | GitHub Actions (ruff + pytest) |
| Fonts | Bundled proprietary Microsoft fonts | System fonts |
| Chinese stack | Routes through OpenAI | Native Qwen/CosyVoice/CogVideoX (local GPU, no API keys) |
| Distribution | GitHub only | GitHub + Gitee-ready (Mandarin README) |

## Creative System

### Trope Prompt Director (R10)
YAML-defined viral video patterns injected into the LLM prompt. The director selects tropes based on video type, topic, and target audience, then modifies the system prompt to guide script generation toward proven viral structures.

### Intro Contrast Packs
TikTok-native attention patterns:
- IKEA narrator (deadpan Scandinavian delivery)
- ASMR whisper × loud bass drop
- Nature documentary ("here we observe the...")
- Elevator music × heavy metal transition
- Alpine serenity × loud mariachi
- Wholesome setup × horror audio sting

### Videographer Rules Engine
Professional editing patterns, codified:
- Hook: first 3 seconds, separate scene, close shot
- Pacing: clamped by video type (tutorial 5-30s, documentary 6-40s)
- B-roll: auto-inserted after 3 consecutive A-roll segments
- Transitions: cut/crossfade/fade-black by scene type and context
- Duration rebalancing: scenes scaled to hit target total

### Screening Room (R3)
VLM self-critique loop. After rendering, a vision-language model watches the output video and generates structured feedback on pacing, visual coherence, audio sync, and engagement. The feedback can trigger re-rendering of weak segments.

## Surfaces

### MCP Tools
`videogen_generate`, `videogen_plan`, `videogen_plan_render`, `videogen_status`, `videogen_list_jobs`, `videogen_providers`, `videogen_depot`, `videogen_settings`

### REST API
`/health`, `/api/v1/generate`, `/api/v1/plan`, `/api/v1/plan/render`, `/api/v1/jobs`, `/api/v1/jobs/{id}`, `/api/v1/jobs/{id}/download`, `/api/v1/providers`, `/api/v1/depot`, `/api/v1/settings`, `/api/v1/publish`, `/api/v1/logs`, `/api/v1/tools`, `/api/v1/status`

### Webapp (React + Vite, port 11055)
Dashboard, Generate, Plan, Jobs, Depot, Settings, Logs, Help, Publish, Chat, API Docs, Status, Tools

### Desktop (Tauri 2.0)
Single-click NSIS installer, 31 MB. Embeds PyInstaller-frozen backend + React dist. No Python/Node/uv on target machine.

## Setup Experience

### End user
Download `roughcut_0.1.0_x64-setup.exe` → double-click → use.

### Developer
```
git clone → just go
```
`start.ps1` auto-detects and installs Python, uv, FFmpeg, creates .env, starts server, opens browser.

## Remaining Work

- Gitee mirror with Mandarin community
- CI-built Tauri installer (currently manual `native/build.ps1`)
- Hybrid free-stock fallback (try Pexels → Pixabay → Coverr per scene)
- E2E Playwright tests for webapp
- Production demo videos showcasing mid-length output
- Upload post-rebrand NSIS to GitHub Release

## Verdict

Architecturally superior to MoneyPrinterTurbo. Creatively more ambitious (trope director, screening room, intro contrast packs). The plugin system held through 14+ providers without architectural strain. 193+ tests from a repo that started as an afternoon project.

The question is not whether it's good enough. The question is whether discovery finds it.

---

*Assessment by Sandra Schipal, 2026-06-13, Vienna.*
*Scaffold: opencode (deepseek-v4-pro). Extension: Cursor. Build/debug/release: opencode.*
