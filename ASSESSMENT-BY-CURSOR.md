# ittybitty / videogen-mcp — Assessment by Cursor

**Date:** 2026-06-12 (rev 3)  
**Assessed by:** Cursor (Composer)  
**Audience:** Continuing agents (Fable, DeepSeek, Sandra)  
**Repo path:** `D:\Dev\repos\videogen-mcp`  
**GitHub remote:** `https://github.com/sandraschi/ittybittyvideos.git` (private)  
**Product:** **ittybitty**  
**Version:** **0.2.0** (`pyproject.toml`)  
**HEAD:** `fed4b77` — `Rebrand to ittybitty and simplify README for end users.`  
**Working tree:** clean (post-push)  
**Supersedes:** rev 2 (stale uncommitted / Fable-timeout narrative)

---

## Read this first

1. **Naming is settled** — product **ittybitty**; Python stays `videogen_mcp`; env `VIDEOGEN_*`; native `ittybitty-native.exe` / `ittybitty-backend.exe`; Tauri id `ai.fleet.ittybitty`. Do not reopen.  
2. **User docs vs agent docs** — [README.md](./README.md) is short/end-user facing. This file, [TODO.md](./TODO.md), [docs/GITIGNORE-ASSESSMENT.md](./docs/GITIGNORE-ASSESSMENT.md), [SPEC.md](./SPEC.md) are for agents.  
3. **Before `src/` batch edits** — `git log -1` exists; run `uv run pytest -q` after Python changes.  
4. **Append to agent log** (§ Agent log) when closing P0/P1 items.

---

## Executive summary (rev 3)

**ittybitty** is a shippable **0.2.0 MVP+**:

| Area | State |
|------|--------|
| Short + mid-length pipelines | ✅ |
| SQLite job + depot | ✅ `job_store.py`, `depot.db` |
| SOTA webapp (13 pages) | ✅ committed |
| Publish handoff API | ✅ |
| Fleet Logs page + ring buffer | ✅ |
| Settings UI + `.env` persistence | ✅ |
| Stock: Pexels, Veo/Omni, LocalGen, **Jellyfin, Plex** | ✅ |
| Windows NSIS + Tauri sidecar | ✅; backend spawn fixed (resources path) |
| Dev launch (Vite :11055 + API :11054) | ✅ |
| Tests | ✅ **113** (`uv run pytest -q`) |
| R1 alignment / karaoke ASS | ✅ committed |
| R2 beat snap | ⚠️ `audio.py` + compose ducking exist; **not wired** in pipeline; no `beats` extra |
| Golden demo video in README | ⏳ GSD puppy short planned; legacy cats MP4 still in git (~1.7 MB) |
| pyright clean | ⚠️ verify with `uv run pyright src/` |
| mcpb packaging | ❌ deferred |

**Verdict:** Ship and iterate. Next leverage = finish **R2 wiring**, **demo asset hygiene**, **YouTube Shorts upload (Tier 2 publish)**.

---

## Naming (do not reopen)

| Layer | Name |
|-------|------|
| Product | **ittybitty** |
| GitHub | `sandraschi/ittybittyvideos` |
| Folder | `videogen-mcp` |
| Package / MCP | `videogen-mcp` / `videogen_*` |
| Env | `VIDEOGEN_*` |
| Tauri | `ittybitty-native`, identifier `ai.fleet.ittybitty` |
| Install dir | `%LOCALAPPDATA%\ittybitty\` |
| Spawn log | `%LOCALAPPDATA%\ai.fleet.ittybitty\logs\backend-spawn.log` |

---

## Reconciliation (rev 3)

Verified 2026-06-12: `git log -1`, `uv run pytest -q` → **113 passed**, `*.bak` count **0**.

| Claim | Status | Notes |
|-------|--------|-------|
| rev 2 “uncommitted webapp” | **Stale** | Committed in `45ca9e4` / `dd36bb0` / `e414b3a` |
| rev 2 “in-memory jobs” | **Stale** | SQLite `job_store` + depot |
| rev 2 “64 tests” | **Stale** | **113** tests |
| rev 2 “20 *.bak files” | **Fixed** | 0 on disk; `*.bak` gitignored |
| R2 beat snap | **Partial** | `services/audio.py`; not imported by pipeline |
| R2 music ducking | **Partial** | `compose.py` sidechain; pipeline may not pass BGM path consistently |
| Tauri backend spawn | **Fixed** | `fed4b77` era — resolve `resources/ittybitty-backend.exe` |
| NSIS staging wrong exe | **Fixed** | `build.ps1` matches version suffix |
| Jellyfin/Plex library stock | **Done** | `stock_library.py`, settings UI |
| Private repo CI workflow | **In git, disabled on GitHub** | run locally per fleet policy |
| README embedded demo video | **Removed** | poster/MP4 deferred; see [TODO.md](./TODO.md) |

---

## Architecture map (current)

```
src/videogen_mcp/
  server.py                 FastAPI + MCP + SPA + settings/logs/publish API
  services/
    pipeline.py             short jobs → job_store
    pipeline_extended.py    mid-length
    job_store.py            SQLite persistence ✅
    depot.py                library scan/import
    planner.py / videographer.py
    compose.py              FFmpeg + karaoke ASS + ducking (R2 partial)
    align.py                R1 whisper alignment ✅
    audio.py                R2 beats ⚠️ unwired
    jellyfin_library.py / plex_library.py / library_clips.py
    publish.py              social handoff ✅
    google_video.py         Veo/Omni bridge
webapp/src/pages/           13 routes (Dashboard, Generate, Plan, Jobs, Depot, Publish, Settings, Help, Logs, …)
native/                     Tauri + PyInstaller + NSIS
tests/                      113 passed
```

---

## P0 — Do next

| ID | Item | Notes |
|----|------|-------|
| P0-1 | **Wire R2 beats** | `[project.optional-dependencies] beats = ["librosa>=0.10"]`; pipeline imports `detect_beats` / `snap_cut_durations`; `tests/test_audio.py` |
| P0-2 | **GSD puppy demo** | Short vertical sample; poster JPG in README only (no embedded `<video>`); see gitignore assessment for MP4 policy |
| P0-3 | **Rebuild NSIS after rebrand** | Binary names now `ittybitty-*`; upload new release asset |
| P0-4 | **pyright** | Run `uv run pyright src/`; fix any regressions in `tts_edge.py` if still failing |

---

## P1 — High value

| ID | Item |
|----|------|
| P1-1 | Mocked FFmpeg integration test (compose argv) |
| P1-2 | YouTube Shorts resumable upload (Publish Tier 2) |
| P1-3 | Trim or gitignore `docs/examples/*.mp4` (keep poster + release attachment) |
| P1-4 | mcpb package (deferred but spec’d in INSTALL) |

---

## P2 — Hygiene

- Sync [mcp-central-docs/projects/ittybitty](../mcp-central-docs/projects/ittybitty/) version row to **0.2.0** when cutting release notes  
- `webapp/dist/` stays gitignored; Tauri/`just build-native` builds it  
- `native/resources/*.exe` gitignored via `native/.gitignore` — build sidecar before Tauri  
- No GitHub Actions on private repo (fleet policy) — workflow file is template only  

---

## Webapp inventory (committed)

| Page | Purpose |
|------|---------|
| Dashboard | Health, providers, recent jobs |
| Generate | Short video |
| Plan | Mid-length storyboard + render |
| Jobs | Progress + publish link |
| Depot | SQLite library, posters |
| Publish | Caption pack, platform URLs |
| Settings | LLM/stock/TTS + Jellyfin/Plex |
| Logs | Fleet ring buffer |
| Help | Tabbed user guide |
| Tools / Chat / Status / API Docs | MCP + REST helpers |

Start: `.\start.bat` or `just go` · Dev UI **11055** · API/MCP **11054**

---

## Standards conformance

| Standard | Status |
|----------|--------|
| FastMCP ≥3.2 | ✅ |
| Ports 11054/11055 | ✅ MCD registered |
| WEBAPP_SOTA | ✅ |
| ruff | ✅ |
| pytest | ✅ 113 |
| Job persistence | ✅ SQLite |
| Tauri fleet spawn pattern | ✅ (post resources-path fix) |
| mcp-central-docs project page | ✅ `projects/ittybitty/` |
| pyright | ⚠️ verify |
| mcpb | ❌ deferred |

---

## What NOT to build yet

R3 Screening Room, R4 arXiv grounding, R5 semantic match, R6 storyboard editor overhaul — blocked on **R2 complete** + **golden demo** unless Sandra reprioritizes.

---

## Agent log

| Date | Agent | Action |
|------|-------|--------|
| 2026-06-12 | Cursor | rev 1 assessment; 59 tests |
| 2026-06-12 | Fable 5 | R1 commit; R2 partial; timeout |
| 2026-06-12 | Cursor | rev 2 assessment (pre-commit sprawl) |
| 2026-06-12 | Cursor | v0.2.0: webapp, depot, NSIS, Jellyfin/Plex, Tauri fix |
| 2026-06-12 | Cursor | Rebrand → **ittybitty**; README simplification; **rev 3** assessment |

---

## MCD (fleet mirror)

| Doc | Path |
|-----|------|
| Project page | `mcp-central-docs/projects/ittybitty/README.md` |
| Competition | `mcp-central-docs/projects/ittybitty/COMPETITIVE_ANALYSIS.md` |
| Gitignore fleet standard | `mcp-central-docs/standards/GITIGNORE_STANDARDS.md` |

---

## Verdict (rev 3)

**ittybitty is in good shape for 0.2.0.** The repo’s enemy is no longer uncommitted sprawl — it’s **finishing R2**, **lean demo assets**, and **publish automation**. Read [TODO.md](./TODO.md) for the ordered backlog.
