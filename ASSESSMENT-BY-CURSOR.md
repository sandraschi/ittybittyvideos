# roughcut / videogen-mcp — Assessment by Cursor

**Date:** 2026-06-12 (rev 2 — post-Fable timeout)  
**Assessed by:** Cursor (Composer)  
**Audience:** Fable 5 (resume after 5h timeout), DeepSeek v4, any continuing agent  
**Repo path:** `D:\Dev\repos\videogen-mcp`  
**GitHub remote:** `https://github.com/sandraschi/roughcut.git` (private)  
**Version assessed:** 0.1.0  
**HEAD commit:** `9ed0a75` — `feat(R1): universal word-level subtitles via faster-whisper forced alignment + karaoke ASS captions`  
**Working tree:** **dirty** — webapp, publish API, R2 partial, doc drift (see § Uncommitted work)  
**Supersedes:** rev 1 (same day; pre-R1 commit, pre-webapp)

---

## Fable 5 — resume here (5h timeout)

Fable likely died mid-**SPEC R2** (beat snap + music ducking):

| R2 piece | State | File |
|----------|--------|------|
| Music ducking (sidechaincompress) | **In compose, uncommitted** | `services/compose.py` — `_build_audio_filter`, `duck`/`duck_ratio` params |
| Beat detection + snap | **Module written, not wired** | `services/audio.py` (untracked) — `detect_beats`, `snap_cut_durations` |
| librosa extra | **Missing** | `pyproject.toml` has `align` extra only; needs `beats = ["librosa>=0.10"]` |
| Beat tests | **Missing** | No `tests/test_audio.py` |
| Pipeline integration | **Not done** | `pipeline.py` / `pipeline_extended.py` do not import `audio.py` yet |

**Do not restart R2 from scratch.** Read Fable's `compose.py` diff and finish wiring: BGM path → `detect_beats(bgm)` → `snap_cut_durations` → concat timings. Commit as `feat(R2): beat snap + music ducking` after tests.

**Do not touch** uncommitted `webapp/` or `publish.py` unless merging — Cursor owns that slice; rebase Fable work on top after webapp commit lands.

---

## Instructions for downstream agents

1. Read this file before editing `src/`, README, or SPEC.  
2. Naming is settled (§ Naming) — do not reopen.  
3. **Commit order:** (A) webapp + publish + server API → (B) Fable R2 finish → (C) job persistence.  
4. Do not start SPEC R3–R8 until P1-1 (job store) is closed.  
5. Update reconciliation table + agent log when closing items.

---

## Executive summary

**roughcut** graduated from “afternoon scaffold” to **credible 0.1.0 product skeleton**:

- **R1 shipped** (committed): faster-whisper alignment, karaoke ASS, CosyVoice timing fix path  
- **SOTA webapp** (uncommitted): React/Vite, 10 pages, Publish handoff for TikTok/Shorts/Reels  
- **Publish API** (uncommitted): caption pack, Explorer reveal, platform deep links  
- **64 tests green** (uncommitted +3 publish, +2 status/tools vs 59 at R1 commit)  
- **R2 half-done** (Fable timeout): ducking in compose; beats module orphan  

Still **not production-shippable**: in-memory jobs, no FFmpeg E2E test, no full render demo on disk, README comparison table still says “42 tests”, **20 `*.bak` files** on disk, **4 pyright errors** in `tts_edge.py` (pre-existing).

**Verdict:** Strong momentum. Next win = **two commits** (webapp stack, then R2 finish) + **job persistence**. Not Screening Room.

---

## Naming (do not reopen)

| Layer | Name |
|-------|------|
| Product | **roughcut** |
| GitHub | `roughcut` |
| Package / MCP | `videogen-mcp` / `videogen_*` |
| Env | `VIDEOGEN_*` |
| Tauri | `roughcut-native` |

---

## Reconciliation (claims vs verified state)

Verified 2026-06-12 rev 2: `git log`, source read, `uv run pytest` → **64 passed**.

| Claim | Status | Notes |
|-------|--------|-------|
| 42 tests (README table vs MPT) | **Stale** | Marketing table; body says 59; actual **64** |
| R1 forced alignment | **Done (committed)** | `9ed0a75`, `align.py`, `--extra align` |
| Karaoke ASS subs | **Done (committed)** | `compose.py` `_build_ass_karaoke` |
| CosyVoice word-level | **Fixed via align** | No native word boundaries; align post-pass |
| R2 beat snap | **Partial (Fable WIP)** | `audio.py` untracked; not in pipeline |
| R2 music ducking | **Partial (Fable WIP)** | `compose.py` sidechain; uncommitted |
| SOTA webapp | **Done (uncommitted)** | `webapp/src/` — 10 pages, builds clean |
| Publish / social handoff | **Done (uncommitted)** | `publish.py`, Publish page, `/publish-pack` |
| Mid-length pipeline | **Implemented** | planner + videographer + extended pipeline |
| Job persistence | **Missing** | `_jobs` dict |
| FFmpeg E2E | **Missing** | Unit tests on SRT/align only |
| mcp-central-docs | **Done** | `projects/roughcut/` + competition analysis |
| `*.bak` clutter | **Worse (20 files)** | Delete before next agent session |
| pyright clean | **No** | 4 errors `tts_edge.py` TypedDict (known pre-R1) |

---

## Uncommitted work (2026-06-12 evening)

```
M  ASSESSMENT-BY-CURSOR.md, README.md, SPEC.md, justfile
M  src/videogen_mcp/server.py          # status, tools, publish-pack, reveal, SPA dist
M  src/videogen_mcp/services/compose.py # R2 ducking (Fable)
M  tests/test_server.py
?? src/videogen_mcp/services/audio.py   # R2 beats (Fable)
?? src/videogen_mcp/services/publish.py
?? tests/test_publish.py
?? webapp/                               # full React app + package-lock
```

**Suggested commits:**

1. `feat: SOTA webapp + publish API + social handoff` — webapp, publish, server, justfile, tests, docs  
2. `feat(R2): beat-aware cuts + music ducking` — Fable finishes audio wiring + pyproject beats extra + tests  

---

## P0 — Fix before new features

### P0-1. Commit webapp + publish slice (Cursor)

Single commit; run before Fable R2 to reduce merge pain:

```powershell
Set-Location D:\Dev\repos\videogen-mcp
uv sync --extra dev
Set-Location webapp; npm run build; Set-Location ..
uv run pytest -q
# git add webapp/ publish.py test_publish.py server.py justfile README SPEC ASSESSMENT
```

### P0-2. Finish R2 (Fable resume)

- Add `[project.optional-dependencies] beats = ["librosa>=0.10"]`  
- Wire `detect_beats` + `snap_cut_durations` in `pipeline.py` when BGM present  
- `tests/test_audio.py` for snap monotonicity + tolerance  
- Env: `VIDEOGEN_BEAT_SNAP`, `VIDEOGEN_DUCK_DB` per SPEC  

### P0-3. Sync README numbers

| Location | Fix |
|----------|-----|
| README MPT table | “42 tests” → “64+ tests” |
| README Dev section | “59 tests” → “64 tests” |
| README-zh.md | Same |
| pyproject description | Mention mid-length + MCP |

### P0-4. Delete `*.bak` files (20 on disk)

Gitignored but agents read them. PowerShell:

```powershell
Get-ChildItem -Path D:\Dev\repos\videogen-mcp -Recurse -Filter *.bak | Remove-Item -Force
```

### P0-5. Fix pyright in `tts_edge.py` (4 errors)

TypedDict optional keys — use `.get()` or narrow type. Blocks `just check` green run.

---

## P1 — High value next

| ID | Item | Why |
|----|------|-----|
| P1-1 | **SQLite job store** | Restart-safe; Publish page useful after reboot |
| P1-2 | **Mocked FFmpeg integration test** | Prove compose argv without real encode |
| P1-3 | **One golden render** | Goliath: topic → mp4 → Publish page screenshot/GIF |
| P1-4 | **YouTube Shorts upload (Tier 2)** | Best API ROI for automated publish |

---

## P2 — Hygiene

- Commit `webapp/package-lock.json`; keep `webapp/dist/` gitignored (build locally or in Tauri pipeline)  
- Apps Hub / Skill page — deferred (no skills provider yet); OK for 0.1.0  
- mcpb packaging — deferred  
- No GitHub Actions — correct for private repo  

---

## Webapp inventory (uncommitted, SOTA-aligned)

| Page | Purpose |
|------|---------|
| Dashboard | Health, providers, Ollama probe, recent jobs |
| Short video | 30–60s generate, 9:16 default |
| Mid-length | Plan preview + render |
| Jobs | Poll progress → link to Publish |
| **Publish** | Download, caption copy, Explorer reveal, platform URLs |
| Tools | MCP catalog via `/api/v1/tools` |
| Chat | REST quick generate/plan |
| Status | JSON audit |
| API Docs | Swagger/ReDoc iframe |
| Help | Setup + publish tiers |

Start: `webapp/start.ps1` or `just stack` · Dev :11055 · API :11054

---

## Publishing strategy (minimum fuss)

| Tier | Status | Method |
|------|--------|--------|
| 1 | **Shipped (uncommitted)** | Publish page + `publish-pack` API |
| 2 | Planned v0.2 | YouTube Data API resumable Shorts upload |
| 3 | Future | TikTok Content Posting API (OAuth + review) |
| 4 | Future | Postiz schedule-once → many platforms |

Generate **9:16** for TikTok/Reels/Douyin; **16:9** for YouTube long / LinkedIn.

---

## Architecture map (current)

```
src/videogen_mcp/
  server.py              FastAPI + MCP + webapp SPA + publish/status/tools API
  services/
    pipeline.py          short jobs (in-memory)
    pipeline_extended.py mid-length
    planner.py           LLM storyboard
    videographer.py      editing rules ← core IP
    compose.py           FFmpeg + karaoke ASS + ducking (R2 partial)
    align.py             R1 whisper alignment ✅
    audio.py             R2 beats ⚠️ untracked, unwired
    publish.py           social handoff ⚠️ uncommitted
    cache.py
webapp/                  React SOTA ⚠️ uncommitted
native/                  Tauri + NSIS
tests/                   64 passed
```

---

## Standards conformance

| Standard | Status |
|----------|--------|
| FastMCP ≥3.2 | ✅ |
| Ports 11054/11055 | ✅ registered in MCD |
| WEBAPP_SOTA (React/Vite/Tailwind) | ✅ uncommitted |
| ruff | ✅ |
| pyright | ❌ 4 known errors |
| pytest | ✅ 64 |
| mcp-central-docs | ✅ |
| Job persistence | ❌ |
| mcpb | ❌ deferred |

---

## What NOT to build (unchanged)

R3 Screening Room, R4 arXiv grounding, R5 semantic match, R6 storyboard editor — all blocked on P1-1 + golden render.

---

## Suggested agent split (post-timeout)

| Agent | Own | Avoid |
|-------|-----|-------|
| **Cursor / Sandra** | Commit webapp + publish (P0-1), README sync | Rewriting R2 compose |
| **Fable 5 (resume)** | Finish R2 wiring + tests (P0-2) | Rebuilding webapp |
| **DeepSeek v4** | P1-1 job SQLite **after** above commits | Parallel pipeline edits |

---

## Agent log

| Date | Agent | Action |
|------|-------|--------|
| 2026-06-12 | Cursor (Composer) | rev 1 assessment; 59 tests; R1 pre-commit |
| 2026-06-12 | Fable 5 | R1 commit `9ed0a75`; R2 partial (audio.py, compose ducking); **5h timeout** |
| 2026-06-12 | Cursor (Composer) | SOTA webapp + publish API (uncommitted); rev 2 assessment |

---

## Verdict (rev 2)

**roughcut is going great** — R1 landed, webapp + publish path exist, Fable left R2 on the 10-yard line. The repo's enemy is now **uncommitted sprawl** and **agent backup files**, not architecture.

**Next 2 hours for a human or agent:** commit webapp → Fable finishes R2 → delete `.bak` → job SQLite → one demo video through Publish.

---

## MCD (canonical fleet mirror)

| Doc | Path |
|-----|------|
| Project page | `mcp-central-docs/projects/roughcut/README.md` |
| Competition | `mcp-central-docs/projects/roughcut/COMPETITIVE_ANALYSIS.md` |
