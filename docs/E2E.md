# End-to-end tests (Playwright)

Browser smoke tests live under `webapp/e2e/`. They assume the **backend is running on port 11054** and the dev UI on **11055** (Vite proxies `/api` and `/health` to the backend).

---

## One-time setup

```powershell
Set-Location D:\Dev\repos\videogen-mcp\webapp
npm install
npx playwright install chromium
```

---

## Run (recommended)

Terminal 1 — backend + Vite (from repo root):

```powershell
Set-Location D:\Dev\repos\videogen-mcp
.\start.bat
```

Terminal 2 — Playwright:

```powershell
Set-Location D:\Dev\repos\videogen-mcp\webapp
npm run e2e
```

Or use the helper script (starts backend if needed, then runs tests):

```powershell
Set-Location D:\Dev\repos\videogen-mcp
.\scripts\run-e2e.ps1
```

---

## Built webapp on :11054

After `npm run build` in `webapp/` and serving via the Python app (no Vite):

```powershell
$env:ITTYBITTY_E2E_BASE_URL = "http://127.0.0.1:11054"
Set-Location D:\Dev\repos\videogen-mcp\webapp
npm run e2e
```

---

## What is covered

| Spec | Checks |
|------|--------|
| `smoke.spec.ts` | Dashboard, Status JSON, Help, Tools page (7 MCP tools incl. `videogen_review`) |

Not covered yet: full generate render, depot upload, Settings save (need keys / long jobs).

---

## Python API tests

FastAPI integration tests remain in `tests/` (`uv run pytest -q`). E2E complements those with real browser routing and React Query fetches.
