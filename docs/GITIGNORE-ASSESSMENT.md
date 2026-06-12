# .gitignore assessment — ittybitty (`videogen-mcp`)

**Date:** 2026-06-12  
**Audience:** Agents and maintainers  
**Fleet standard:** [mcp-central-docs/standards/GITIGNORE_STANDARDS.md](../../mcp-central-docs/standards/GITIGNORE_STANDARDS.md)

---

## Summary

Root + `native/.gitignore` cover the important cases. No `node_modules/` or `.venv/` in git. A few **optional tightenings** below (demo MP4s, build artifacts).

**Grade:** ✅ Good — safe for day-to-day commits.

---

## Root `.gitignore` (verified)

| Pattern | Purpose | Status |
|---------|---------|--------|
| `__pycache__/`, `*.pyc` | Python bytecode | ✅ |
| `.venv/` | uv/pip env | ✅ |
| `.env` | Secrets | ✅ **never commit** |
| `output/`, `cache/`, `test_output/`, `test_cache/` | Renders and test artifacts | ✅ |
| `dist/`, `build/` | PyInstaller / packaging | ✅ |
| `*.spec` | PyInstaller spec (local edits OK) | ✅ |
| `node_modules/` | npm | ✅ |
| `webapp/dist/` | Vite production build | ✅ build in CI/Tauri |
| `*.bak` | Agent backup clutter | ✅ |
| `.ruff_cache/`, `.pytest_cache/`, `.pyright/` | Tool caches | ✅ |
| `*.tsbuildinfo` | TS incremental | ✅ |
| `server_err.log` | Local debug | ✅ |

---

## `native/.gitignore`

| Pattern | Purpose | Status |
|---------|---------|--------|
| `resources/*.exe` | PyInstaller sidecar (large) | ✅ build via `build-sidecar.ps1` |
| `binaries/*.exe` | Dev triple copy | ✅ |
| `target/` | Rust/Tauri build | ✅ |

---

## Tracked but worth revisiting

| Path | Issue | Recommendation |
|------|--------|----------------|
| `docs/examples/cats-facts-short.mp4` | ~1.7 MB in git; README no longer embeds it | **P1:** `git rm --cached` + add `docs/examples/*.mp4` to `.gitignore`; ship demos via GitHub Release assets |
| `docs/examples/cats-facts-short-poster.jpg` | ~150 KB | ✅ keep for future README thumbnail |
| `webapp/package-lock.json` | Large but correct | ✅ commit (reproducible npm ci) |

---

## Not gitignored (intentional)

| Path | Why tracked |
|------|-------------|
| `.github/workflows/ci.yml` | Template for public/future CI |
| `native/Cargo.lock` | Reproducible Rust builds |
| `uv.lock` | Reproducible Python deps |
| `webapp/src/` | Source of truth for UI |

---

## Pre-commit checklist (agents)

```powershell
Set-Location D:\Dev\repos\videogen-mcp
git status
# Must NOT appear: .env, output/, node_modules/, webapp/dist/, dist/*.exe, native/resources/*.exe
uv run ruff check src tests
uv run pytest -q
```

If `git status` shows unexpected binaries:

```powershell
git restore --staged path\to\file
# or add pattern to .gitignore then git rm --cached
```

---

## Recovery (if secrets or node_modules were committed)

Follow [GITIGNORE_STANDARDS.md](../../mcp-central-docs/standards/GITIGNORE_STANDARDS.md) — rotate keys, `git filter-repo` or BFG for history rewrite if needed.

---

## Suggested follow-up (optional)

1. Add to root `.gitignore`: `docs/examples/*.mp4` (keep `!docs/examples/README.md`)  
2. Document demo asset location in [examples/README.md](./examples/README.md)  
3. Never commit `%LOCALAPPDATA%\ittybitty\` or user `.env` from installed app  

---

*Update this file when `.gitignore` rules change.*
