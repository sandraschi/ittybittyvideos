# Development — ittybitty

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
| `align` | faster-whisper for word-level subtitles (R1) |
| `beats` | librosa for beat snap + ducking (R2) |
| `google` | Direct Google Veo/Omni clients |
| `dev` | pytest, ruff, pyright |

Browser e2e: see [docs/E2E.md](./E2E.md) (`webapp/` Playwright smoke tests).

Provider links: [docs/EXTERNAL-REFERENCES.md](./EXTERNAL-REFERENCES.md).

---

## Run backend

```powershell
py -m videogen_mcp.server
```

Or `.\start.bat` (Vite **11055** + API **11054** — fleet dev stack).

- Dev UI: http://127.0.0.1:11055/
- API docs: http://127.0.0.1:11054/docs
- MCP: http://127.0.0.1:11054/mcp
- Health: http://127.0.0.1:11054/health

---

## Webapp dev

**Default:** `start.bat` or `just go` — starts backend + Vite together.

**Manual split:**

```powershell
just backend          # API only :11054
just web              # Vite only :11055 (backend must already run)
```

Vite on **11055** proxies `/api`, `/health`, `/mcp`, etc. to **11054**.

**Release / single-port** (Tauri, PyInstaller):

```powershell
just build-web
just backend
```

Output goes to `webapp/dist/` — served by FastAPI at `/` on **11054**.

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

## Continuous integration

Workflow: [`.github/workflows/ci.yml`](../.github/workflows/ci.yml) — **one job** on `windows-latest` (mirrors `just check` + webapp `tsc`):

1. `uv sync --extra dev`
2. `pre-commit run --all-files` (Ruff + basic hygiene)
3. `uv run pyright src/`
4. `uv run pytest -q`
5. `npm ci` + `npx tsc --noEmit` + `npm run build` in `webapp/`

**Triggers:** push to `main`, **`v*`** tags, pull requests, manual dispatch.

**Public repo:** [`sandraschi/ittybittyvideos`](https://github.com/sandraschi/ittybittyvideos).

### Pre-commit (local)

After clone:

```powershell
just bootstrap
# or: uv sync --extra dev; uv run pre-commit install
```

Hooks run automatically on `git commit`. Manual full scan:

```powershell
uv run pre-commit run --all-files
```

Local equivalent before push:

```powershell
just check
Push-Location webapp
npm ci
npx tsc --noEmit
npm run build
Pop-Location
```

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

Private repos: GitHub Actions disabled by fleet policy — see [Continuous integration](#continuous-integration) above and `CHANGELOG.md`. Build installers locally.

---

## Ports (fleet registry)

| Service | Port |
|---------|------|
| ittybitty backend | 11054 |
| Vite dev | 11055 |
| LocalGen sidecar | 8188 |

Update `mcp-central-docs/ports/WEBAPP_PORTS.md` if these change.
