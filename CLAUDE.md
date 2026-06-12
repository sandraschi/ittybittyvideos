# Claude project context — ittybitty

Mirrors [AGENTS.md](AGENTS.md). Read [ASSESSMENT-BY-CURSOR.md](ASSESSMENT-BY-CURSOR.md) before large changes.

**What it is:** MCP + REST video generator — script from LLM, footage from Pexels / Jellyfin / Plex / cloud / local GPU, TTS, FFmpeg compose, SQLite depot. Windows desktop app available.

**Run locally:**

```powershell
cd videogen-mcp
uv sync --extra dev
.\start.bat
```

Dashboard: http://127.0.0.1:11055 · API/MCP: http://127.0.0.1:11054

**User docs:** [README.md](README.md) · [INSTALL.md](INSTALL.md)  
**Agent docs:** [TODO.md](TODO.md) · [SPEC.md](SPEC.md) · [docs/GITIGNORE-ASSESSMENT.md](docs/GITIGNORE-ASSESSMENT.md)

**Tests:** `uv run pytest -q`

**Do not commit:** `.env`, API keys, `output/`, `native/resources/*.exe`, `webapp/dist/`.
