# Changelog

All notable changes to **ittybitty** (`videogen-mcp`) are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).  
Versioning tracks the Python package in `pyproject.toml`.

---

## [Unreleased]

### Added

- Alpha release path: README badge + warning, marketing site banner, [docs/ALPHA-RELEASE-CHECKLIST.md](docs/ALPHA-RELEASE-CHECKLIST.md), GitHub Pages static site in `docs/` (`index.html`, `.nojekyll`).

### Changed

- **Rebrand:** product name **ittybitty** (was roughcutvideos); native binaries `ittybitty-native.exe` / `ittybitty-backend.exe`; Tauri identifier `ai.fleet.ittybitty`; GitHub repo `sandraschi/ittybitty`.

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
