# Claude project context — ittybitty

This file mirrors [AGENTS.md](AGENTS.md) for Claude Code / Desktop sessions.

**What it is:** MCP + REST video generator — script from LLM, footage from Pexels or local Wan 2.2, TTS, FFmpeg compose, SQLite depot.

**Run locally:**

```powershell
cd videogen-mcp
pip install -e .
.\start.bat
```

Dashboard: http://127.0.0.1:11055 (dev) · API/MCP: http://127.0.0.1:11054

**Docs:** [README.md](README.md) · [INSTALL.md](INSTALL.md) · [docs/TOOLS.md](docs/TOOLS.md) · [SPEC.md](SPEC.md)

**Tests:** `py -m pytest`

**Do not commit:** `.env`, API keys, `output/` renders unless explicitly requested.
