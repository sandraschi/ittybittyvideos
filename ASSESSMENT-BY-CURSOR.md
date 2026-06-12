# roughcut / videogen-mcp — Assessment by Cursor

**Date:** 2026-06-12  
**Assessed by:** Cursor (Composer)  
**Audience:** Fable 5, DeepSeek v4, and any agent continuing this repo  
**Repo path:** `D:\Dev\repos\videogen-mcp`  
**GitHub remote:** `https://github.com/sandraschi/roughcut.git` (private)  
**Version assessed:** 0.1.0 (last commit `2042d52`; **dirty working tree** — see § Uncommitted work)  
**Supersedes:** n/a (first cross-agent assessment)

---

## Instructions for downstream agents

Read this file **before** editing `src/`, README, or SPEC. Do not re-litigate naming (§ Naming). Do not start SPEC R3–R8 features until P0/P1 items here are closed. Prefer **consolidation over expansion**. When you finish a tracked item, update the reconciliation table and add your agent id + date to § Agent log.

---

## Executive summary

**roughcut** is a credible **0.1.0 MVP scaffold**: FastMCP 3.2 + FastAPI, short-form pipeline, mid-length planner + videographer rules, seven provider plugins, Tauri/NSIS shell, and **59 passing unit tests**. Architecture is genuinely better than MoneyPrinterTurbo-style monoliths.

It is **not yet production-shippable**: jobs are in-memory only, there are no integration/E2E tests (FFmpeg, APIs), docs are stale vs working tree, and R1 alignment work is **uncommitted**. The SPEC roadmap (R1–R8) is a multi-week product plan sitting on a one-day codebase — treat it as backlog, not current scope.

**Naming is settled:** product = **roughcut**; Python/MCP package = **videogen-mcp** (`videogen_*` tools, `VIDEOGEN_*` env). Do not rename the package unless Sandra explicitly asks.

---

## Naming (do not reopen)

| Layer | Name | Notes |
|-------|------|-------|
| Product / brand | **roughcut** | README title, Tauri app, GitHub repo |
| Python package | `videogen-mcp` / `videogen_mcp` | Fleet MCP convention |
| MCP server id | `videogen-mcp` | Tool prefix `videogen_*` |
| Env prefix | `VIDEOGEN_*` | Keep for fleet consistency |
| Local folder | `videogen-mcp` | OK; rename optional |
| Native crate | `roughcut-native` | Tauri sidecar |

**Rule:** User-facing copy says *roughcut*. Code/API/MCP stays *videogen*.

---

## Reconciliation (claims vs verified state)

Verified 2026-06-12 via source read + `uv run pytest` (59 passed).

| Claim (README / SPEC) | Status | Evidence |
|----------------------|--------|----------|
| 42 tests | **Stale** | 59 tests pass; +17 from uncommitted `align` work |
| Mid-length 3–15 min pipeline | **Implemented** | `planner.py`, `videographer.py`, `pipeline_extended.py` |
| Plugin registry (7 providers) | **Implemented** | `providers/*.py`, `test_providers.py` |
| CosyVoice word-level subs | **Partial** | R1 `align.py` wired in `pipeline.py`; **not committed** |
| edge-tts word timestamps | **Implemented** | `tts_edge.py` + compose karaoke path |
| Webapp UI | **Skeleton only** | Single static `webapp/dist/index.html`; no Vite/React source |
| Tauri NSIS installer | **Scaffolded** | `native/` built; release artifacts in tree |
| MCP at `/mcp` | **Implemented** | `server.py` mounts `mcp.http_app()` |
| Job persistence | **Missing** | `_jobs: dict` in `pipeline.py` — lost on restart |
| FFmpeg compose | **Implemented, untested E2E** | `compose.py` shells out; tests cover SRT helpers only |
| CogVideoX / CosyVoice local | **HTTP stubs** | No CI/integration proof against real servers |
| SPEC R2–R8 | **Not started** | Roadmap only |
| `*.bak` agent backups | **Present on disk** | 16 files; gitignored but clutter agents |

---

## P0 — Fix before new features

### P0-1. Commit or revert the R1 alignment WIP

**Dirty files (2026-06-12):**

```
M  README.md, pyproject.toml, uv.lock
M  config/settings.py, providers/base.py, providers/tts_edge.py
M  services/compose.py, pipeline.py, pipeline_extended.py
?? services/align.py, tests/test_align.py
```

`align.py` is good work (optional `faster-whisper`, honest `None` fallback, difflib canonical mapping). **Either:**

1. **Commit as one coherent R1 slice** (`feat: R1 forced alignment + karaoke compose`), or  
2. **Stash/revert** if another agent is redoing R1 differently.

Do **not** leave two agents editing `pipeline.py` / `compose.py` in parallel without reading each other's diffs.

### P0-2. Sync docs to implementation

After P0-1 lands, update in the **same PR/commit**:

| File | Fix |
|------|-----|
| `README.md` | Test count → 59; document `uv sync --extra align`; FFmpeg required on PATH |
| `README-zh.md` | Same test count |
| `SPEC.md` | Mark R1 partial/complete; note `videogen_align`, `videogen_sub_style` |
| `pyproject.toml` | Description still says "short video" only — mention mid-length |

### P0-3. Delete `*.bak` files from disk

16 timestamped backups under `src/`, root. Already in `.gitignore`. **Delete them.** They cause agents to read stale code and re-introduce reverted logic.

---

## P1 — High value, small scope

### P1-1. Durable job store

Replace in-memory `_jobs` with SQLite or JSON files under `videogen_output_dir`. Minimum: persist `job_id`, `status`, `progress`, `output_path`, `error`, `created_at`. Required before Tauri/desktop "actually ships" claim.

### P1-2. One integration test (mocked FFmpeg)

Add `tests/test_compose_integration.py` that mocks `subprocess.run` and asserts FFmpeg argv includes expected scale/subtitle filters. Proves compose wiring without requiring FFmpeg in CI (private repo = no GH Actions anyway; still valuable locally).

### P1-3. Document hard dependencies

Add to README **Requirements**:

- FFmpeg on PATH (compose hard-fails without it)
- Optional: `uv sync --extra align` for faster-whisper
- API keys: `OPENAI_API_KEY`, `PEXELS_API_KEY` (defaults)

### P1-4. Run `just check` before handoff

```powershell
Set-Location D:\Dev\repos\videogen-mcp
uv sync --extra dev --extra align
just check
```

Fix any ruff/pyright regressions from R1 WIP before claiming done.

---

## P2 — Hygiene & drift

- **`webapp/dist/`** is gitignored but a committed-looking `index.html` exists — clarify in SPEC: static placeholder until R6 React editor.
- **`native/target/`** — ensure fully gitignored; don't commit Rust build artifacts.
- **CORS `allow_origins=["*"]`** — fine for local MCP; document if desktop webview needs tighter origins later.
- **No mcpb manifest yet** — deferred per SPEC; don't half-add unless Sandra wants fleet packaging now.
- **No CI** — correct for private repo per fleet standards; local `just check` is the gate.

---

## What is genuinely good (preserve)

1. **Videographer rules engine** (`services/videographer.py`) — real differentiator vs short-form clones; well-tested.
2. **One-file-per-provider registry** — clean extension point; adding DeepSeek LLM = ~40 lines in `providers/llm_deepseek.py`.
3. **Mid-length planner** — chaptered storyboard is the product thesis; don't collapse back to single-script mode.
4. **Honest optional deps** — `align.py` IMPLEMENTATION_HONESTY pattern; replicate for future features.
5. **Dual surface** — REST + MCP on one FastAPI app matches fleet SOTA.
6. **Tone / positioning** — roughcut brand vs MPT is clear; keep voice, fix facts.

---

## What NOT to build next (agent trap list)

| Temptation | Why skip now |
|------------|--------------|
| SPEC R3 Screening Room (VLM critique) | Needs working E2E render + job persistence first |
| SPEC R4 arXiv grounding | Large scope; arxiv-mcp exists — integrate later |
| SPEC R5 semantic footage matching | Premature without eval set + baseline renders |
| SPEC R6 full React storyboard editor | Big UI project; backend scene cache doesn't exist yet |
| Rename package to `roughcut-mcp` | Breaks tool names unless Sandra approves fleet-wide |
| Add GitHub Actions | Private repo — fleet norm is no CI |
| More README shitposting | Fine for marketing; fix stale numbers first |

**Recommended next feature after P0/P1:** SPEC **R2** (beat-aware cuts + music ducking) *or* finish **R1** karaoke acceptance test with a real audio fixture — not R3+.

---

## Architecture map (for agents new to the tree)

```
src/videogen_mcp/
  server.py              FastAPI + FastMCP tools + REST
  config/settings.py     pydantic-settings (VIDEOGEN_*)
  models/schema.py       short-form job/request types
  models/storyboard.py   mid-length plan types
  providers/             @register_llm|stock|tts plugins
  services/
    pipeline.py          short jobs (in-memory _jobs)
    pipeline_extended.py mid-length render
    planner.py           LLM storyboard
    videographer.py      post-LLM editing rules  ← core IP
    compose.py           FFmpeg concat + subs
    align.py             R1 whisper alignment (WIP, uncommitted)
    cache.py             footage cache
native/                  Tauri roughcut-native + build.ps1
webapp/dist/             static HTML placeholder UI
tests/                   unit tests only (59)
```

**Entry:** `uv run python -m videogen_mcp.server` → `http://127.0.0.1:11054/health`

---

## Standards conformance (fleet)

| Standard | Status |
|----------|--------|
| FastMCP ≥3.2 | ✅ |
| Port 11054 | ✅ |
| 12-factor env (`VIDEOGEN_*`) | ✅ |
| Portmanteau / tool count reasonable | ✅ (6 tools) |
| ruff + pytest + pyright | ✅ (`just check`) |
| Private repo — no GH Actions | ✅ (none present) |
| mcp-central-docs alignment | ⚠️ not cross-linked yet |
| mcpb packaging | ❌ deferred |
| Implementation honesty (optional deps) | ✅ in align.py |
| Git checkpoint before batch edits | ⚠️ R1 WIP uncommitted |

---

## Minimal spin-up (verified)

```powershell
Set-Location D:\Dev\repos\videogen-mcp
Copy-Item .env.example .env   # add OPENAI_API_KEY, PEXELS_API_KEY
uv sync --extra dev
uv sync --extra align         # optional, for R1 alignment
just dev                      # or: uv run python -m videogen_mcp.server
```

Requires **FFmpeg** on PATH. Without API keys, LLM/stock steps fail at runtime (expected).

---

## Suggested work split (Fable 5 / DeepSeek v4)

| Agent | Own | Avoid |
|-------|-----|-------|
| **Whoever touched R1 last** | Finish P0-1, P0-2, P0-3; run `just check` | Starting R2/R3 in same session |
| **Other agent** | P1-1 job persistence **or** P1-2 integration test | Editing same files as R1 commit |
| **Either** | `providers/llm_deepseek.py` if Sandra wants DeepSeek | Renaming repo/package |

**Merge rule:** One agent commits R1; second agent rebases on that before pipeline/compose edits.

---

## Agent log

| Date | Agent | Action |
|------|-------|--------|
| 2026-06-12 | Cursor (Composer) | Initial assessment; 59 tests verified; R1 WIP noted uncommitted |

*(Append rows when you close P0/P1 items.)*

---

## Verdict

**Keep the name roughcut.** Keep the package videogen-mcp. The codebase is a strong day-one foundation with a videographer rules engine that actually matters — but two LLMs sprinting on the same afternoon left backup files, stale README numbers, and uncommitted overlapping edits. **Next session = consolidate, not expand.** Ship R1 + job persistence before any "Screening Room" dreams.
