# Changelog

All notable changes to **ittybitty** (`videogen-mcp`) are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).  
Versioning tracks the Python package in `pyproject.toml`.

---

## [Unreleased]

### Added

- **Free stock parity (MPT):** `pixabay` and `coverr` stock providers — same plugin pattern as Pexels; Settings keys `PIXABAY_API_KEY`, `COVERR_API_KEY`.
- Alpha release path: README badge + warning, marketing site banner, [docs/ALPHA-RELEASE-CHECKLIST.md](docs/ALPHA-RELEASE-CHECKLIST.md), GitHub Pages static site in `docs/` (`index.html`, `.nojekyll`).
- R10 planning: [docs/PROMPT-DIRECTOR.md](docs/PROMPT-DIRECTOR.md) (mermaid), webapp **Prompt library** (`/prompts`) with sample topics + localStorage CRUD.
- **Webapp Director UX:** collapsed **Director (optional)** panel with 8 curated recipes; full trope/intro pack lists behind “Show all packs”; **Length** presets (~15–50 s) on the default Generate path (`director-recipes.ts`, `DirectorOptions.tsx`, `short-length.ts`).
- **MCP catalog:** `videogen_mcp.mcp_registry.MCP_TOOL_CATALOG` (16 tools) — single source for `/api/v1/tools`, `/health`, `/api/v1/status`.
- **MCP tools:** `videogen_help`, `videogen_intros`, `videogen_credits`, `videogen_visual_look`, `videogen_depot`, `videogen_publish_pack`; `visual_style` / `visual_material` / `visual_tone` on generate and plan tools.
- **MCP tests:** `tests/test_mcp.py`; shared `client` fixture in `tests/conftest.py`.
- **Validation harness:** `scripts/validate_fable.py` for live pipeline checks (named for Fable 5 review agent; see MCD ADN-2026-06-12-002).
- **Live validation (Fable 5, 2026-06-13):** R1/R2/R3 passed end-to-end on run `a9e798ffba86` (screening flagged hook, clip replaced, recomposed).

### Changed

- **Docs/TODO sync:** refreshed tracker, provider docs, and MPT free-stock comparison (3 free APIs).
- **NSIS rebuild (2026-06-14):** `dist/ittybitty-0.2.0-x64-setup.exe` (33.2 MB) — Pixabay/Coverr + Director UX + 16 MCP tools.
- **Rebrand:** product name **ittybitty** (was roughcutvideos); native binaries `ittybitty-native.exe` / `ittybitty-backend.exe`; Tauri identifier `ai.fleet.ittybitty`; GitHub repo `sandraschi/ittybitty`.
- **MCP docs:** [docs/TOOLS.md](docs/TOOLS.md) lists all 16 tools; README points agents to `videogen_help` first.
- Intro/credits MCP samples accept `intro:` / `credits:` prefixes and optional `seed`.

### Fixed

- **`/health` / status `tool_count`:** was stuck at 7; now reflects the full MCP catalog (16 when FastMCP is loaded).
- **Whisper align:** CUDA → CPU fallback when `cublas64_12` (or GPU libs) are missing.
- **Beat snap (`librosa` 0.11 / NumPy 2.4):** tempo ndarray handling in `snap_cut_durations`.
- **Planner JSON:** tolerant parse for DeepSeek trailing commas in storyboard responses.
- **Compose diagnostics:** ffmpeg failures under load dump stderr to `*.ffmpeg-error.log`.

### Known issues (live validation)

- Empty-narration scenes (`voice_006` gap) can cause A/V drift after that scene (subtitle timing assumes contiguous audio).
- Default screening VLM: `gemma4:e4b` validated; prefer `gemma4:12b` when pulled (26b does not fit 4090).

---

## [0.2.0] — 2026-06-12

### Added

- **Windows NSIS desktop app:** `native/build.ps1` → `dist/ittybitty-{version}-x64-setup.exe`; PyInstaller sidecar via `native/build-sidecar.ps1`; upload via `scripts/publish-release-local.ps1` or `just publish-release`.
- **Personal library footage:** stock providers `jellyfin` and `plex` — search your media server and ffmpeg-cut B-roll from home videos (same credentials as fleet MCPs).
- **Google cloud footage:** stock providers `veo` (Veo 3.x) and `omni` (Gemini Omni Flash) via `google-ai-mcp` bridge or direct API (`pip install -e ".[google]"`).
- **Fleet Logs page:** `/logs` UI + `/api/logs` ring buffer (filter, live tail, export, clear).
- **Help page:** horizontal tabs (pipeline, footage tiers, depot, publish, MCP, troubleshooting).
- **README stack:** `INSTALL.md`, `AGENTS.md`, `CLAUDE.md`, `docs/*`, shipped demo MP4 under `docs/examples/`.
- **Depot:** SQLite persistence (`depot.db`), scan/import, posters, web UI.
- **Settings UI:** multi-LLM providers (DeepSeek, OpenAI, LM Studio, Ollama), stock probes, Jellyfin/Plex credentials, `.env` persistence.
- **LocalGen sidecar:** Wan 2.2 default (`localgen`); legacy `cogvideo` alias retained.
- Minimal **Windows CI** workflow (`.github/workflows/ci.yml`).

### Changed

- **Dev launch is fleet-standard:** `start.bat` / `just go` runs Vite on **:11055** + API on **:11054** — no stale `webapp/dist` required.
- Backend serves built UI at `/` only after `just build-web` (Tauri / single-port releases).
- Removed auto-build of `webapp/dist` from `start.ps1`; native `build.ps1` runs `build-web` first.
- Product branding → **ittybitty** (package remains `videogen_mcp`).
- FFmpeg concat uses absolute paths; edge-tts duration via ffprobe fallback.

### Fixed

- **Tauri backend spawn:** resolve `resources/ittybitty-backend.exe` (plex-mcp pattern) instead of a missing flat exe beside the main binary.
- **NSIS staging:** `build.ps1` picks the version-matched installer bundle, not a stale `ittybitty_0.1.0_*` artifact.
- Windows render path resolution for FFmpeg concat lists.

---

## [0.1.0] — 2026-06-12

### Added

- Short (30–60 s) and mid-length (3–15 min) video pipelines.
- Plugin LLM / stock / TTS providers (OpenAI, Ollama, Pexels, Edge TTS).
- FastMCP 3.2 + FastAPI backend on port **11054**; React/Vite webapp on **11055** (dev).
- MCP tools: `videogen_generate`, `videogen_plan`, `videogen_plan_render`, `videogen_status`, `videogen_list_jobs`, `videogen_providers`.
- Publish handoff API and SOTA dashboard (Generate, Jobs, Plan, Publish, Tools, Chat, Status).
