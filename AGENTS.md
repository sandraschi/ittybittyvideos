# Agent notes — ittybitty (`videogen-mcp`)

## Identity

| Field | Value |
|-------|--------|
| Product | **ittybitty** |
| Folder | `videogen-mcp` |
| Python package | `videogen_mcp` |
| Backend port | **11054** (Vite dev UI **11055**) |
| LocalGen sidecar | **8188** |
| GitHub | `sandraschi/ittybittyvideos` |

## Internal docs (read before big edits)

| Doc | Use |
|-----|-----|
| [ASSESSMENT-BY-CURSOR.md](./ASSESSMENT-BY-CURSOR.md) | Current state, reconciliation, P0/P1 |
| [TODO.md](./TODO.md) | Ordered backlog |
| [docs/GITIGNORE-ASSESSMENT.md](./docs/GITIGNORE-ASSESSMENT.md) | What must not be committed |
| [SPEC.md](./SPEC.md) | Architecture and roadmap R1–R8 |

## Before editing

1. Read [ASSESSMENT-BY-CURSOR.md](./ASSESSMENT-BY-CURSOR.md) and [SPEC.md](SPEC.md).
2. Follow [mcp-central-docs/standards/README_STRUCTURE.md](../mcp-central-docs/standards/README_STRUCTURE.md) for doc changes.
3. Run `uv run pytest -q` after Python changes.
4. Do **not** commit `.env`, API keys, `output/`, or `native/resources/*.exe`.

## Key modules

| Area | Path |
|------|------|
| FastAPI + MCP mount | `src/videogen_mcp/server.py` |
| Short pipeline | `src/videogen_mcp/services/pipeline.py` |
| Mid-length pipeline | `src/videogen_mcp/services/pipeline_extended.py` |
| Job persistence | `src/videogen_mcp/services/job_store.py`, `depot.py` |
| Library stock (Jellyfin/Plex) | `services/jellyfin_library.py`, `plex_library.py`, `providers/stock_library.py` |
| Settings / `.env` | `services/config_store.py`, `settings_api.py` |
| Tauri spawn | `native/src/backend.rs` |
| Webapp | `webapp/src/pages/` |

## Provider registry

- **LLM:** deepseek, openai, lmstudio, ollama (+ custom script bypasses LLM)
- **Stock:** pexels (default), jellyfin, plex, veo, omni, localgen (cogvideo alias)
- **TTS:** edge-tts (default), cosyvoice optional

## Conventions

- Minimal diffs; match FastMCP 3.2 + FastAPI patterns.
- User-facing strings and native binaries: **ittybitty**; Python package stays `videogen_mcp`.
- No GitHub Actions on private repos (fleet policy).
- PowerShell on Windows — no `&&` in scripts shown to the user.

## Docs map

- **Users:** [README.md](README.md), [INSTALL.md](INSTALL.md), [CHANGELOG.md](CHANGELOG.md), `docs/*.md`, in-app `/help` and `/logs`
- **Agents:** this file, ASSESSMENT, TODO, GITIGNORE-ASSESSMENT, SPEC
- **Fleet:** `mcp-central-docs/projects/ittybitty/`
