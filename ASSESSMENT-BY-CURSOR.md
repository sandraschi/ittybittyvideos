# ittybitty / videogen-mcp — Assessment by Cursor

**Date:** 2026-06-12 (rev 4)  
**Assessed by:** Cursor (Composer)  
**Audience:** Continuing agents (Fable, DeepSeek, Sandra)  
**Repo path:** `D:\Dev\repos\videogen-mcp`  
**GitHub remote:** `https://github.com/sandraschi/ittybittyvideos.git` (private)  
**Product:** **ittybitty**  
**Version:** **0.2.0** (`pyproject.toml`)  
**HEAD (local):** `191abbe` — `feat(R3): Screening Room` (+ 2 unpushed commits below)  
**Working tree:** Fable WIP — uncommitted `align.py`, `audio.py`, `planner.py`, `scripts/validate_fable.py`  
**Supersedes:** rev 3 (stale: 113 tests, R2 unwired)

---

## Read this first

1. **Naming is settled** — product **ittybitty**; Python stays `videogen_mcp`; env `VIDEOGEN_*`; native `ittybitty-native.exe` / `ittybitty-backend.exe`; Tauri id `ai.fleet.ittybitty`. Do not reopen.  
2. **User docs vs agent docs** — [README.md](./README.md) is short/end-user facing. This file, [TODO.md](./TODO.md), [docs/GITIGNORE-ASSESSMENT.md](./docs/GITIGNORE-ASSESSMENT.md), [SPEC.md](./SPEC.md) are for agents.  
3. **Before `src/` batch edits** — `git log -1` exists; run `uv run pytest -q` after Python changes.  
4. **Append to agent log** (§ Agent log) when closing P0/P1 items.

---

## Executive summary (rev 4)

**ittybitty** is **0.2.0 MVP++** with Fable’s R2/R3/R9 landed locally (3 commits **not pushed**):

| Area | State |
|------|--------|
| Short + mid-length pipelines | ✅ |
| SQLite job + depot | ✅ |
| SOTA webapp (13 pages) | ✅ |
| Stock: Pexels, Veo/Omni, LocalGen, Jellyfin, Plex | ✅ |
| Windows NSIS + Tauri sidecar | ✅ (release v0.2.0 on GitHub) |
| **R1** alignment / karaoke ASS | ✅ |
| **R2** beat snap + ducking | ✅ wired in `pipeline.py` (`bc2b519`) |
| **R3** Screening Room VLM | ✅ code + tests; live VLM validation pending |
| **R9** talking-head PiP | ✅ plumbing; external `TALKER_URL` backend pending |
| Tests | ✅ **145** (`uv run pytest -q`) |
| Playwright e2e smoke | ✅ scaffold (`webapp/e2e/`, rev 4 Cursor) |
| Provider/model docs | ✅ [docs/PROVIDERS-AND-MODELS.md](./docs/PROVIDERS-AND-MODELS.md) |
| Golden demo video | ⏳ GSD puppy short planned |
| R4–R8 | ❌ not started |

**Verdict:** Fable finished **runs 2–3** (R2+R9, then R3). He is now on **live-validation / hardening** (uncommitted CUDA→CPU align fallback, librosa numpy fix, planner respects `VIDEOGEN_LLM_PROVIDER`, `validate_fable.py`). Do **not** edit those four paths in parallel without merging his WIP first.

---

## Fable session map (2026-06-12)

| Commit / artifact | SPEC | What shipped |
|-------------------|------|--------------|
| `bc2b519` | **R2 + R9** | `detect_beats`/`snap_cut_durations` in short pipeline; sidechain duck in compose; `beats` extra; `talker_sadtalker.py`, `overlay.py`, post-pass in `pipeline.py` |
| `191abbe` | **R3** | `critic.py`, `videogen_review`, screening loop in `pipeline_extended.py`, `tests/test_critic.py` |
| WIP (uncommitted) | **R1/R3 validation** | CUDA→CPU whisper retry; audio tempo fix; planner uses configured LLM; `scripts/validate_fable.py` (phase1 short + phase2 screening) |

**Which “run”?** Not R4 yet. Fable is between **R3 commit** and **validate_fable live run** — effectively a **validation run**, not the next SPEC feature phase.

### Conflict zones (hands off for other agents)

- `src/videogen_mcp/services/align.py`, `audio.py`, `planner.py`
- `scripts/validate_fable.py`
- Already committed but Fable-owned: `critic.py`, `pipeline.py`, `pipeline_extended.py`, `overlay.py`, `talker_sadtalker.py`

### Safe parallel work

- Docs (`docs/*`, `ASSESSMENT`, Help page copy)
- Playwright e2e (`webapp/e2e/`)
- New pytest that mocks FFmpeg / VLM (no pipeline edits)
- R4+ only after Fable WIP is committed and Sandra reprioritizes

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

## Reconciliation (rev 4)

Verified 2026-06-12: `git log -3`, `uv run pytest -q` → **145 passed**; local **ahead of origin by 3** (`eb9cf6b`, `bc2b519`, `191abbe`).

| Claim | Status | Notes |
|-------|--------|-------|
| rev 3 “R2 unwired” | **Stale** | Wired in `bc2b519`; `beats` extra in pyproject |
| rev 3 “113 tests” | **Stale** | **145** after R2/R3/R9 tests |
| R3 Screening Room | **Done (code)** | Live gemma/qwen VLM run pending |
| R9 talking head | **Plumbing done** | Needs `TALKER_URL` service ~:11100 |
| Fable validate script | **WIP** | `scripts/validate_fable.py` untracked |
| Tauri / NSIS / rebrand | **Done** | Release v0.2.0 on GitHub |

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
    compose.py              FFmpeg + karaoke ASS + ducking ✅
    align.py                R1 whisper alignment ✅ (Fable WIP: CUDA fallback)
    audio.py                R2 beats ✅ (Fable WIP: numpy/librosa fix)
    critic.py               R3 VLM screening ✅
    overlay.py              R9 PiP ✅
  providers/talker_sadtalker.py  R9 HTTP contract ✅
tests/                      145 passed · webapp/e2e Playwright smoke (Cursor rev 4)
```

---

## P0 — Do next

| ID | Item | Notes |
|----|------|-------|
| P0-1 | **Commit + push Fable stack** | 3 local commits + WIP align/audio/planner/validate_fable |
| P0-2 | **Live validation** | `uv run python scripts/validate_fable.py` (needs BGM, Ollama VLM, Pexels) |
| P0-3 | **R9 talker backend** | Wrapper on ~:11100; Settings UI fields |
| P0-4 | **GSD puppy demo** | Short vertical sample for README poster |
| P0-5 | **Rebuild NSIS** | After Fable work lands |

---

## P1 — High value

| ID | Item |
|----|------|
| P1-1 | Playwright e2e in CI-like script | `scripts/run-e2e.ps1` ✅ scaffold |
| P1-2 | Mocked FFmpeg integration test (compose argv) |
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
| pytest | ✅ 145 |
| Job persistence | ✅ SQLite |
| Tauri fleet spawn pattern | ✅ (post resources-path fix) |
| mcp-central-docs project page | ✅ `projects/ittybitty/` |
| pyright | ⚠️ verify |
| mcpb | ❌ deferred |

---

## What NOT to build yet

**R4–R8** (source grounding, semantic match, storyboard editor, templates, fleet bridge) until Fable WIP is merged and live R1–R3 validation passes. Other agents: prefer docs/tests over pipeline edits.

---

## Agent log

| Date | Agent | Action |
|------|-------|--------|
| 2026-06-12 | Cursor | rev 1 assessment; 59 tests |
| 2026-06-12 | Fable 5 | R1 commit; R2 partial; timeout |
| 2026-06-12 | Cursor | rev 2 assessment (pre-commit sprawl) |
| 2026-06-12 | Cursor | v0.2.0: webapp, depot, NSIS, Jellyfin/Plex, Tauri fix |
| 2026-06-12 | Fable 5 | R2+R9 (`bc2b519`), R3 (`191abbe`); validation WIP |
| 2026-06-12 | Cursor | rev 4 assessment; PROVIDERS-AND-MODELS.md; Playwright e2e scaffold |

---

## Verdict (rev 4)

**Fable delivered R2, R9 plumbing, and R3.** He paused on **live validation** (3 h timeout), not R4. Cursor can safely extend **docs and e2e**; push Fable’s commits when reviewed. See [TODO.md](./TODO.md) and [docs/PROVIDERS-AND-MODELS.md](./docs/PROVIDERS-AND-MODELS.md).

| Doc | Path |
|-----|------|
| Project page | `mcp-central-docs/projects/ittybitty/README.md` |
| Competition | `mcp-central-docs/projects/ittybitty/COMPETITIVE_ANALYSIS.md` |
| Gitignore fleet standard | `mcp-central-docs/standards/GITIGNORE_STANDARDS.md` |

---

## MCD (fleet mirror)
