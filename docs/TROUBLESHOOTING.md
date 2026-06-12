# Troubleshooting — roughcutvideos

---

## Dashboard & server

### Blank page or "Webapp not built"

**Cause:** `webapp/dist` missing.

**Fix:**

```powershell
cd webapp
npm install
npm run build
```

Or use `start.bat` after a release that includes a built dist.

### Port 11054 already in use

**Fix:** Set `VIDEOGEN_PORT=11056` (or another free port) in `.env` and restart.

### `/mcp` returns 404

**Cause:** FastMCP not installed or import failed.

**Fix:** `pip install -e .` and check logs on startup for FastMCP warnings.

---

## Generation failures

### "Pexels API key" / stock download errors

**Fix:** Add `PEXELS_API_KEY` in **Settings** or `.env`. Verify at [pexels.com/api](https://www.pexels.com/api/).

### LLM topic mode unavailable

**Fix:** Set the matching API key (DeepSeek/OpenAI) or start Ollama/LM Studio and configure base URL in Settings. Use **Custom script** mode to bypass LLM.

### FFmpeg not found

**Fix:** Install FFmpeg (`winget install Gyan.FFmpeg`), reopen terminal, confirm `ffmpeg -version`.

### Job stuck in `fetching_footage`

**Cause:** Slow network, Pexels rate limit, or LocalGen timeout.

**Fix:** Check server logs. For LocalGen, confirm `GET http://127.0.0.1:8188/api/health` returns OK.

---

## LocalGen / GPU

### CUDA out of memory

**Fix:**

- Switch backend to `wan22-5b` in `.env` (`LOCALGEN_BACKEND=wan22-5b`)
- Or use **pexels** stock provider
- Close other GPU applications

### LocalGen sidecar won't start

**Fix:**

```powershell
pip install -e ".[localgen]"
.\start-localgen.bat
```

First run downloads large model weights — ensure disk space and stable network.

### Generated clips are low quality or short

Wan 2.2 quality depends on prompt, steps, and resolution in sidecar config. See `localgen_server/` settings. Hybrid Pexels → AI fallback is planned (SPEC R5) but not default yet.

---

## Depot

### Missing old videos in Depot

**Fix:** Click **Scan output** on Depot page or `POST /api/v1/depot/scan`. Jobs created before SQLite migration may only appear after scan.

### Poster missing

Posters are extracted on compose completion. Re-scan won't regenerate — re-render or delete and recreate.

---

## Subtitles

### Subtitles drift from audio

Install align extra for word-level timing:

```powershell
pip install -e ".[align]"
```

Without it, TTS uses estimated sentence timings.

---

## MCP / Claude

### Claude can't reach server

MCP URL must be reachable from Claude's process. Use `http://127.0.0.1:11054/mcp` only when the server runs on the same machine. Start `py -m videogen_mcp.server` before connecting.

### Tools list empty

Restart MCP client after server start. Confirm `/health` returns OK.

---

## Logs

Server logs go to stderr when run via `py -m videogen_mcp.server`. Increase verbosity:

```env
VIDEOGEN_LOG_LEVEL=DEBUG
```

---

## Still stuck?

1. In-app **Help** → **Troubleshooting** tab  
2. [GitHub Issues](https://github.com/sandraschi/roughcut/issues)  
3. Fleet doc: `mcp-central-docs/projects/roughcutvideos/`
