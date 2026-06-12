# Development — roughcutvideos

---

## Repository layout

```
videogen-mcp/
├── src/videogen_mcp/     # Python backend, providers, pipelines
├── webapp/               # React + Vite dashboard
├── native/               # Tauri shell (optional desktop)
├── tests/
├── output/               # Renders + depot.db (gitignored)
├── start.bat             # Backend + serve dist
└── docs/
```

---

## Python setup

```powershell
cd D:\Dev\repos\videogen-mcp
pip install -e ".[dev]"
```

Optional extras:

| Extra | Purpose |
|-------|---------|
| `localgen` | Torch + diffusers for LocalGen sidecar |
| `align` | faster-whisper for word-level subtitles |
| `tauri` | Desktop packaging deps |

---

## Run backend

```powershell
py -m videogen_mcp.server
```

Or `.\start.bat` (builds/serves webapp if dist present).

- API docs: http://127.0.0.1:11054/docs  
- MCP: http://127.0.0.1:11054/mcp  
- Health: http://127.0.0.1:11054/health  

---

## Webapp dev

```powershell
cd webapp
npm install
npm run dev
```

Vite listens on **11055** and proxies API calls to **11054**. Run the Python server in a second terminal.

Production build:

```powershell
cd webapp
npm run build
```

Output goes to `webapp/dist/` — served by FastAPI at `/`.

---

## LocalGen sidecar

```powershell
pip install -e ".[localgen]"
.\scripts\start_localgen.ps1
```

Endpoints: `GET /api/health`, `POST /api/generate`. Used by `stock_localgen.py`.

---

## Tests

```powershell
py -m pytest
py -m pytest tests/test_job_store.py -v
py -m pytest tests/test_localgen_server.py -v
```

No GPU required for default test suite (LocalGen tests may mock HTTP).

---

## Lint / format

If ruff is installed via dev extras:

```powershell
py -m ruff check src tests
py -m ruff format src tests
```

---

## Adding a provider

1. Create `src/videogen_mcp/providers/stock_foo.py` (or `llm_`, `tts_`).
2. Subclass the base in `providers/base.py`.
3. Register with `@register_stock("foo")` (import side-effect loads registry).
4. Add config fields to `settings.py` / Settings UI if needed.
5. Add tests under `tests/test_providers.py`.

---

## Packaging

- **MCPB:** fleet script or manual bundle per mcp-central-docs packaging guides.
- **Tauri:** see `native/` and [tauri-fleet-expert skill](../../.cursor/skills/tauri-fleet-expert/SKILL.md) for NSIS installer patterns.

Private repos: no GitHub Actions CI (fleet policy). Build installers locally.

---

## Ports (fleet registry)

| Service | Port |
|---------|------|
| roughcutvideos backend | 11054 |
| Vite dev | 11055 |
| LocalGen sidecar | 8188 |

Update `mcp-central-docs/ports/WEBAPP_PORTS.md` if these change.
