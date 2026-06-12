# Configuration — ittybitty

Settings persist in **`.env`** at the repo root. The webapp **Settings** page reads and writes the same file.

Provider homepages and repos: [EXTERNAL-REFERENCES.md](./EXTERNAL-REFERENCES.md).

---

## Core server

| Variable | Default | Description |
|----------|---------|-------------|
| `VIDEOGEN_HOST` | `127.0.0.1` | Bind address |
| `VIDEOGEN_PORT` | `11054` | FastAPI + built webapp + `/mcp` |
| `VIDEOGEN_OUTPUT_DIR` | `./output` | MP4 output and `depot.db` |
| `VIDEOGEN_LOG_LEVEL` | `INFO` | Python logging |

---

## LLM providers (topic → script)

Used when **Generate** mode is a cloud/local LLM topic (not custom script).

| Variable | Provider | Notes |
|----------|----------|-------|
| `DEEPSEEK_API_KEY` | deepseek | Default cloud option in UI |
| `OPENAI_API_KEY` | openai | GPT-family scripts |
| `LMSTUDIO_BASE_URL` | lmstudio | e.g. `http://127.0.0.1:1234/v1` |
| `OLLAMA_BASE_URL` | ollama | e.g. `http://127.0.0.1:11434` |
| `OLLAMA_MODEL` | ollama | Model tag, e.g. `llama3.2` |

**Custom script mode** skips the LLM entirely — paste narration text on the Generate page.

Health probes on Settings reflect whether each provider is reachable and keyed.

---

## Stock footage

| Variable | Default | Description |
|----------|---------|-------------|
| `PEXELS_API_KEY` | — | Required for **pexels** provider |
| `VIDEOGEN_STOCK_PROVIDER` | `pexels` | `pexels`, `veo`, `omni`, `localgen`, or `cogvideo` |
| `LOCALGEN_URL` | `http://127.0.0.1:8188` | LocalGen sidecar base URL |
| `LOCALGEN_BACKEND` | `wan22-14b` | `wan22-14b`, `wan22-5b`, `cogvideo-2b` (legacy) |
| `GOOGLE_AI_MCP_URL` | — | Bridge to fleet google-ai-mcp (e.g. `http://127.0.0.1:11014`) |
| `GOOGLE_API_KEY` | — | Direct Gemini / AI Studio key |
| `GOOGLE_CLOUD_PROJECT` | — | Direct Veo via Vertex AI |
| `GOOGLE_CLOUD_LOCATION` | `us-central1` | Vertex region |
| `GOOGLE_VEO_MODEL` | `veo-3.1-preview-002` | Veo model id |
| `GOOGLE_OMNI_MODEL` | `gemini-omni-flash` | Omni model id |

### Pexels (recommended default)

Free API key, no GPU. The pipeline asks the LLM for search terms, downloads matching clips, caches them under `output/`, and trims to scene length.

### Google Veo / Gemini Omni (cloud AI)

Set `VIDEOGEN_STOCK_PROVIDER=veo` or `omni`. **Recommended:** run [google-ai-mcp](https://github.com/sandraschi/google-ai-mcp) and set `GOOGLE_AI_MCP_URL`. Each scene prompt is sent to Veo (~5–8 s) or Omni (~10 s).

**Direct mode:** `pip install -e ".[google]"` plus `GOOGLE_API_KEY` (Omni) and/or `GOOGLE_CLOUD_PROJECT` (Veo).

### LocalGen (optional GPU)

Run `start-localgen.bat` before setting stock to **localgen**. Each scene prompt is sent to the sidecar; Wan 2.2 generates clips locally. Needs CUDA and sufficient VRAM (~24 GB for 14B).

The registry alias **`cogvideo`** still resolves to the same LocalGen client for backward compatibility.

---

## Text-to-speech

| Variable | Default | Description |
|----------|---------|-------------|
| `VIDEOGEN_TTS_PROVIDER` | `edge-tts` | `edge-tts` or `cosyvoice` |
| `COSYVOICE_URL` | `http://127.0.0.1:9880` | If using CosyVoice |

Edge TTS is free and needs no key. Subtitles are generated from TTS timing (word-level when align extra is installed).

---

## R1 — alignment and subtitles

| Variable | Default | Description |
|----------|---------|-------------|
| `VIDEOGEN_ALIGN` | `true` | Run faster-whisper when TTS lacks word timestamps |
| `VIDEOGEN_SUB_STYLE` | `sentence` | `sentence` or `karaoke` (ASS highlight) |
| `VIDEOGEN_WHISPER_MODEL` | `small` | faster-whisper model size |
| `VIDEOGEN_WHISPER_DEVICE` | `auto` | `auto`, `cuda`, or `cpu` |

Install: `pip install -e ".[align]"`.

---

## R2 — beat snap and music ducking

| Variable | Default | Description |
|----------|---------|-------------|
| `VIDEOGEN_BEAT_SNAP` | `true` | Snap scene cuts to BGM beats (short pipeline + `bgm_url`) |
| `VIDEOGEN_BEAT_TOLERANCE` | `0.4` | Max seconds a cut may shift |
| `VIDEOGEN_DUCK` | `true` | Sidechain-compress BGM under narration |
| `VIDEOGEN_DUCK_RATIO` | `8.0` | FFmpeg sidechaincompress ratio |
| `VIDEOGEN_BGM_VOLUME` | `0.3` | Pre-duck BGM gain |

Install: `pip install -e ".[beats]"`.

---

## R3 — Screening Room (VLM critique)

| Variable | Default | Description |
|----------|---------|-------------|
| `VIDEOGEN_SCREENING_PASSES` | `1` | Passes after mid-length render; `0` = off |
| `VIDEOGEN_VLM_URL` | `http://localhost:11434/v1` | OpenAI-compatible vision endpoint |
| `VIDEOGEN_VLM_MODEL` | `qwen3.5-vl` | Model with image input support |

Skipped with a warning when the VLM is unreachable. Critique JSON: `{job_work_dir}/critique_pass_*.json`.

---

## R9 — talking-head PiP overlay

| Variable | Default | Description |
|----------|---------|-------------|
| `VIDEOGEN_TALKER_PROVIDER` | *(empty)* | Set to `sadtalker` to enable |
| `TALKER_URL` | `http://localhost:11100` | External `POST /generate` service |
| `VIDEOGEN_TALKER_SOURCE` | — | Path to face/source image (PNG/JPG) |
| `VIDEOGEN_TALKER_CORNER` | `bottom-right` | PiP corner |
| `VIDEOGEN_TALKER_SCALE` | `0.28` | Head height as fraction of frame |

See [PROVIDERS-AND-MODELS.md](./PROVIDERS-AND-MODELS.md) for the HTTP contract.

---

## Video defaults

| Variable | Default | Description |
|----------|---------|-------------|
| `VIDEOGEN_ASPECT` | `9:16` | `9:16` (shorts) or `16:9` |
| `VIDEOGEN_TARGET_DURATION` | `45` | Short pipeline target seconds |
| `VIDEOGEN_FPS` | `30` | Output frame rate |

Mid-length jobs use separate duration/chapter settings in the API and **Mid-length** UI.

---

## Example `.env`

```env
VIDEOGEN_PORT=11054
VIDEOGEN_OUTPUT_DIR=./output
PEXELS_API_KEY=your_pexels_key
DEEPSEEK_API_KEY=your_deepseek_key
VIDEOGEN_STOCK_PROVIDER=pexels
VIDEOGEN_TTS_PROVIDER=edge-tts
VIDEOGEN_ASPECT=9:16
```

For Google cloud AI footage:

```env
VIDEOGEN_STOCK_PROVIDER=veo
GOOGLE_AI_MCP_URL=http://127.0.0.1:11014
# Or direct: GOOGLE_API_KEY=... GOOGLE_CLOUD_PROJECT=...
```

For all-local footage:

```env
VIDEOGEN_STOCK_PROVIDER=localgen
LOCALGEN_URL=http://127.0.0.1:8188
LOCALGEN_BACKEND=wan22-14b
```

---

## MCP client config

HTTP MCP (server must be running):

```json
{
  "mcpServers": {
    "ittybitty": {
      "url": "http://127.0.0.1:11054/mcp"
    }
  }
}
```

Environment for the server process should include the same `.env` values (load automatically from repo root when started via `start.bat` / `py -m videogen_mcp.server`).
