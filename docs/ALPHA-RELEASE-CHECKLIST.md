# Alpha release checklist

Use this before making **ittybittyvideos** public or publishing a **pre-release** on GitHub.

Target tag example: **`v0.2.0-alpha.1`** (semver pre-release; bump patch for each alpha drop).

---

## 1. Secrets and history

- [ ] `.env` is gitignored and **never committed** (`git check-ignore -v .env`)
- [ ] Scan history for leaked keys:
  ```powershell
  Set-Location D:\Dev\repos\videogen-mcp
  git log -p --all -S "sk-" -- .
  git log -p --all -S "API_KEY" -- .
  ```
- [ ] Rotate any key that ever appeared in a commit (even if later removed)
- [ ] Confirm `dist/`, `output/`, `*.db`, and installer artifacts are ignored

---

## 2. Code and tests

- [ ] Push all intended commits (Fable R1–R3 stack, docs, webapp)
- [ ] Resolve or stash WIP you do **not** want in alpha (`align.py`, `audio.py`, `planner.py`, `validate_fable.py`)
- [ ] Run unit tests: `uv run pytest` (expect ~145+ pass)
- [ ] Optional smoke render: `py scripts/smoke_render.py`
- [ ] Optional e2e: `.\scripts\run-e2e.ps1`

---

## 3. Version and changelog

- [ ] Bump `pyproject.toml` / package version if needed (e.g. `0.2.0` → `0.2.1` for alpha.2)
- [ ] Add **`[Unreleased]`** or alpha section in `CHANGELOG.md` with known gaps:
  - R3 screening room — needs live VLM validation
  - R9 talker — SadTalker/LivePortrait HTTP backend experimental
  - LocalGen — GPU/CUDA requirements; Wan sidecar optional
- [ ] README alpha banner and badge present

---

## 4. Windows installer (optional attachment)

- [ ] `.\native\build.ps1` (or fleet Tauri protocol) produces `dist/ittybitty-*-x64-setup.exe`
- [ ] Smoke-install on a clean profile or VM
- [ ] Log path works: `%LOCALAPPDATA%\ai.fleet.ittybitty\logs\backend-spawn.log`

---

## 5. GitHub: make repo public

Settings → General → Danger zone → **Change repository visibility** → Public.

Only after section 1 is green.

---

## 6. GitHub Release (pre-release)

1. Create annotated tag:
   ```powershell
   git tag -a v0.2.0-alpha.1 -m "Alpha: under construction"
   git push origin v0.2.0-alpha.1
   ```
2. **Releases → Draft new release** → choose tag `v0.2.0-alpha.1`
3. Check **Set as a pre-release**
4. Title: **ittybitty v0.2.0-alpha.1 — under construction**
5. Body template:

   ```markdown
   ## ⚠️ Alpha — not production-ready

   APIs, MCP tools, and the Windows installer may change without notice.

   ### Works today
   - Topic/script → narrated MP4 (Pexels, Edge TTS, FFmpeg)
   - Web dashboard + MCP on :11054 / :11055
   - Depot, Jobs, Settings, Help
   - Jellyfin/Plex B-roll (bring your own tokens)

   ### Experimental / incomplete
   - R3 screening (local VLM critique)
   - R9 PiP talker (external SadTalker/LivePortrait HTTP)
   - LocalGen Wan 2.2 (CUDA ~24 GB)

   ### You need
   - FFmpeg, free Pexels key, optional LLM keys — see README

   ### Install
   Attach `ittybitty-*-x64-setup.exe` or clone and `.\start.bat`
   ```

6. Attach installer binary if built

---

## 7. GitHub Pages

Static site lives in **`docs/`** (`index.html`, `style.css`, `.nojekyll`).

1. Settings → Pages → **Build and deployment**
2. Source: **Deploy from a branch**
3. Branch: **`main`** / folder **`/docs`**
4. Save → wait for `https://sandraschi.github.io/ittybittyvideos/`

After editing the marketing copy, sync from source:

```powershell
Copy-Item D:\Dev\repos\videogen-mcp\website\index.html D:\Dev\repos\videogen-mcp\docs\index.html -Force
Copy-Item D:\Dev\repos\videogen-mcp\website\style.css D:\Dev\repos\videogen-mcp\docs\style.css -Force
```

---

## 8. Repo metadata (optional)

- Description: `Alpha — topic/script → narrated MP4. Windows app, web UI, MCP.`
- Topics: `video`, `ffmpeg`, `mcp`, `shorts`, `tts`, `pexels`
- Disable Wiki if unused
- Issues: enable for alpha feedback

---

## 9. CI (public repo only)

`.github/workflows/ci.yml` may run on public repos (free minutes). Keep jobs minimal — build NSIS locally per fleet habit. Do **not** add GPU or heavy macOS runners without approval.

---

## Quick reference

| Item | URL |
|------|-----|
| Repo | https://github.com/sandraschi/ittybittyvideos |
| Pages | https://sandraschi.github.io/ittybittyvideos/ |
| Releases | https://github.com/sandraschi/ittybittyvideos/releases |
| Fleet docs | https://github.com/sandraschi/mcp-central-docs/tree/main/projects/ittybitty |
