# Installing roughcutvideos

Topic-or-script → rendered MP4 with optional MCP and a built-in dashboard. Repo path: `videogen-mcp`.

---

## Prerequisites

| Tool | Required for | Windows | Notes |
|------|-------------|---------|-------|
| **Python 3.10+** | Options C, D, desktop | [python.org](https://www.python.org/downloads/) or `winget install Python.Python.3.12` | |
| **FFmpeg** | All renders | `winget install Gyan.FFmpeg` | Must be on `PATH` |
| **Node.js 18+** | Webapp dev only | `winget install OpenJS.NodeJS` | Not needed for `start.bat` if `webapp/dist` exists |
| **uv** | Optional faster installs | `winget install astral-sh.uv` | |
| **CUDA GPU ~24 GB** | LocalGen (Wan 2.2) only | — | Pexels workflow needs no GPU |

After winget installs, **close and reopen PowerShell** so PATH updates apply.

**API keys (typical):**

- [Pexels API](https://www.pexels.com/api/) — free stock footage (recommended default)
- [DeepSeek](https://platform.deepseek.com/) or [OpenAI](https://platform.openai.com/) — topic → script (or use custom script / local Ollama)

---

## Option A — Desktop launcher (fastest)

No Claude required. Full dashboard at port 11054.

```powershell
git clone https://github.com/sandraschi/roughcut.git videogen-mcp
cd videogen-mcp
pip install -e .
.\start.bat
```

Open **http://127.0.0.1:11054**. Configure keys in **Settings** (writes `.env`).

**Pass criteria:** Dashboard loads; **Generate** accepts a topic; job appears under **Jobs** / **Depot**.

---

## Option B — MCPB (Claude Desktop)

When a `.mcpb` release is published:

1. Download `{roughcutvideos}-*.mcpb` from [Releases](https://github.com/sandraschi/roughcut/releases)
2. Drag onto Claude Desktop and accept the install prompt
3. Set `PEXELS_API_KEY` and LLM keys in the MCPB env panel
4. Restart Claude Desktop

**Pass criteria:** MCP tools `videogen_*` appear; health check succeeds.

---

## Option C — Manual Claude / Cursor MCP (HTTP)

roughcutvideos exposes MCP over **HTTP** on the same port as the REST API. Start the server first:

```powershell
cd D:\path\to\videogen-mcp
pip install -e .
py -m videogen_mcp.server
```

Add to your MCP config (Cursor `mcp.json` or equivalent):

```json
{
  "mcpServers": {
    "roughcutvideos": {
      "url": "http://127.0.0.1:11054/mcp"
    }
  }
}
```

Use env vars or `.env` in the repo root for API keys. See [docs/CONFIGURATION.md](docs/CONFIGURATION.md).

---

## Option D — Developer mode

```powershell
git clone https://github.com/sandraschi/roughcut.git videogen-mcp
cd videogen-mcp
pip install -e ".[dev,localgen]"
py -m pytest
```

Optional LocalGen sidecar (GPU):

```powershell
.\scripts\start_localgen.ps1
```

See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for Vite dev server, Tauri, and packaging.

---

## Optional: LocalGen (Wan 2.2)

All-AI footage without Pexels:

```powershell
pip install -e ".[localgen]"
.\start-localgen.bat
```

Default URL: `http://127.0.0.1:8188`. In **Settings**, stock provider → **localgen**.

Legacy alias **cogvideo** still registers but points at the same sidecar; prefer **localgen**.

---

## Verify installation

1. **Health:** `GET http://127.0.0.1:11054/health` → `"status": "ok"`
2. **Providers:** Dashboard **Settings** or MCP tool `videogen_providers`
3. **Smoke render:** Generate a 30 s clip on topic `"test sunset"` with Pexels + Edge TTS

In Claude, try:

> *"List videogen providers and generate a 30-second video about cats using Pexels."*

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Blank dashboard | Run `cd webapp; npm run build` or use a release with `webapp/dist` |
| FFmpeg not found | Install FFmpeg; reopen terminal |
| Pexels errors | Set `PEXELS_API_KEY` in Settings |
| LocalGen OOM | Use `wan22-5b` backend or stay on Pexels |
| Port in use | Change `VIDEOGEN_PORT` in `.env` |

Full guide: [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md).
