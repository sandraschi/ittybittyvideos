# ittybitty

**Type a topic → get a narrated video.** Short clips for TikTok/Shorts, or longer explainers with chapters. Works as a Windows app or from source.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## Contents

| | |
|---|---|
| [Get started](#get-started) | Install and first render |
| [What you need](#what-you-need) | Keys and optional extras |
| [Footage sources](#footage-sources) | Where B-roll comes from |
| [More help](#more-help) | Detailed docs (config, dev, MCP, fixes) |

---

## Get started

### Windows app (easiest)

1. Download **`ittybitty-0.2.0-x64-setup.exe`** from [Releases](https://github.com/sandraschi/ittybitty/releases/latest)
2. Install → open **ittybitty** from Start or your desktop shortcut
3. **Settings** → add a [Pexels](https://www.pexels.com/api/) key (free), then **Generate** with a topic or paste a script

Install folder: `%LOCALAPPDATA%\ittybitty\`

### From source (developers)

```powershell
git clone https://github.com/sandraschi/ittybitty.git videogen-mcp
cd videogen-mcp
.\start.bat
```

Open **http://127.0.0.1:11055** (dashboard). API and MCP on **11054**.

Full install paths: [INSTALL.md](INSTALL.md)

---

## What you need

| For | You need |
|-----|----------|
| **Most workflows** | [FFmpeg](https://ffmpeg.org/) on PATH + free **Pexels** API key |
| **Topic → script** | DeepSeek or OpenAI key, or paste your own script |
| **Home videos as B-roll** | Jellyfin or Plex URL + token ([Settings](docs/CONFIGURATION.md)) |
| **Local AI clips (GPU)** | CUDA ~24 GB + `.\start-localgen.bat` |

Everything else is optional. The in-app **Help** page walks through each step.

---

## Footage sources

Pick one in **Settings → Footage**:

- **Pexels** — free stock (default, no GPU)
- **Jellyfin / Plex** — cut clips from your own library (vacation, pets, …)
- **Veo / Omni** — Google cloud (see [config](docs/CONFIGURATION.md))
- **LocalGen** — Wan 2.2 on your GPU

Finished videos land in `./output/` and show up in **Depot**.

---

## Sample output

Demo reel coming soon (GSD puppy short). Until then, run a quick test:

```powershell
py scripts/smoke_render.py
```

Details: [docs/examples/README.md](docs/examples/README.md)

---

## More help

| Doc | When to read it |
|-----|-----------------|
| [INSTALL.md](INSTALL.md) | MCPB, Claude/Cursor MCP, verification |
| [docs/CONFIGURATION.md](docs/CONFIGURATION.md) | All env vars and providers |
| [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | Something broke |
| [docs/TOOLS.md](docs/TOOLS.md) | MCP tools and REST API |
| [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) | Tests, Tauri installer, CI |
| [SPEC.md](SPEC.md) | Architecture and roadmap |
| [CHANGELOG.md](CHANGELOG.md) | Version history |

**MCP:** after the server is running, point your client at `http://127.0.0.1:11054/mcp`.

**Fleet docs:** [mcp-central-docs/projects/ittybitty](https://github.com/sandraschi/mcp-central-docs/tree/main/projects/ittybitty)

---

MIT · [sandraschi](https://github.com/sandraschi) · v0.2.0

*Repo folder `videogen-mcp`, Python package `videogen_mcp` — names stay for MCP compatibility.*
