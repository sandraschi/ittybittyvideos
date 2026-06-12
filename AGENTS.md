# Agent notes — ittybitty (`videogen-mcp`)

## Identity

| Field | Value |
|-------|--------|
| Product | **ittybitty** |
| Folder | `videogen-mcp` |
| Python package | `videogen_mcp` |
| Backend port | **11054** (Vite dev UI **11055**) |
| LocalGen sidecar | **8188** |
| GitHub | `sandraschi/ittybitty` |

## Before editing

1. Read [SPEC.md](SPEC.md) for pipeline architecture.
2. Follow [mcp-central-docs/standards/README_STRUCTURE.md](../mcp-central-docs/standards/README_STRUCTURE.md) for doc changes.
3. Run `py -m pytest` from repo root after Python changes.
4. Do **not** commit `.env` or API keys.

## Key modules

| Area | Path |
|------|------|
| FastAPI + MCP mount | `src/videogen_mcp/server.py` |
| Short pipeline | `src/videogen_mcp/services/pipeline.py` |
| Mid-length pipeline | `src/videogen_mcp/services/pipeline_extended.py` |
| Job persistence | `src/videogen_mcp/services/job_store.py`, `depot.py` |
| Settings / `.env` | `src/videogen_mcp/services/config_store.py`, `settings_api.py` |
| Stock LocalGen | `src/videogen_mcp/providers/stock_localgen.py` |
| LocalGen sidecar | `src/videogen_mcp/localgen_server/` |
| Webapp | `webapp/src/pages/` |

## Provider registry

- **LLM:** deepseek, openai, lmstudio, ollama (+ script mode bypasses LLM)
- **Stock:** pexels (default), localgen (alias cogvideo → same sidecar)
- **TTS:** edge-tts (default), cosyvoice optional

## Conventions

- Minimal diffs; match existing FastMCP 3.2 + FastAPI patterns.
- User-facing strings and native binaries use **ittybitty**; Python package remains `videogen_mcp`.
- No GitHub Actions on private repos (fleet policy).
- PowerShell on Windows — no `&&` in scripts shown to the user.

## Docs map

- User: [README.md](README.md), [INSTALL.md](INSTALL.md), [CHANGELOG.md](CHANGELOG.md), `docs/*.md`, in-app `/help` and `/logs`
- Fleet: `mcp-central-docs/projects/ittybitty/`
