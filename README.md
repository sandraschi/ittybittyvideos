# roughcut

Your film school dropout that actually ships. Topic in, video out. No degree required.

> *"We built this in an afternoon. It has more tests than MoneyPrinterTurbo (86k stars, zero tests). We are not the same."*

## What It Does

You give it a topic. It gives you a video. With narration, stock footage, subtitles, and background music. In HD. While you go make coffee.

**Short mode** (30-60s): TikTok, Reels, Douyin. The usual.

**Mid-length mode** (3-15 min): Tutorials, demos, explainers, documentaries. This is the part nobody else does well. An LLM plans a chaptered storyboard, a videographer rules engine enforces professional pacing (hook, B-roll, transitions, outro), then it renders scene-by-scene.

## The Pipeline

```
"How quantum computing works"
        |
        v
   LLM writes chaptered script with search terms
        |
        v
   Stock footage fetched + cached (or AI-generated via CogVideoX)
        |
        v
   Edge TTS narration with word-level timestamps
   (or CosyVoice — sentence-level today, word-level on the roadmap)
        |
        v
   Videographer rules: hook -> pacing -> B-roll -> transitions -> outro
        |
        v
   FFmpeg compose with burned subtitles
        |
        v
   quantum_computing_tutorial.mp4
```

## vs The Incumbent

| MoneyPrinterTurbo (86k stars) | roughcut |
|------------------------------|----------|
| Zero tests | 42 tests |
| One 2000-line LLM router | Plugin registry (7 providers, one file each) |
| Short-form only (60s max) | **3-15 minute mid-length videos** |
| No scene planning | **Chaptered storyboard + videographer rules** |
| TOML secrets | Env vars (12-factor) |
| Bundled Microsoft fonts (lol) | System fonts |
| g4f reverse-engineering dep | Clean deps only |
| Port 8080 | 11054 |
| No tests, no CI, no lint | ruff + pytest + pyright from day one |

## Chinese Open-Weight Stack

Run the whole thing on your GPU. No API keys. No cloud. No permission.

| Tool | What | How |
|------|------|-----|
| **Qwen 3** | Script generation | `VIDEOGEN_LLM_PROVIDER=qwen` (DashScope or Ollama) |
| **CosyVoice 2** | Mandarin TTS + voice cloning | `VIDEOGEN_TTS_PROVIDER=cosyvoice` |
| **CogVideoX** | AI video clip generation | `VIDEOGEN_STOCK_PROVIDER=cogvideo` |

## Quick Start

```bash
cp .env.example .env
# Add your OPENAI_API_KEY and PEXELS_API_KEY

uv sync
uv run python -m videogen_mcp.server
# http://127.0.0.1:11054/docs
```

## Tools

| Tool | What |
|------|------|
| `videogen_generate` | Short video from topic (30-60s) |
| `videogen_plan` | Plan a mid-length storyboard (preview, no render) |
| `videogen_plan_render` | Plan AND render mid-length video (3-15 min) |
| `videogen_status` | Poll job progress |
| `videogen_list_jobs` | Recent jobs |
| `videogen_providers` | Available LLM/stock/TTS providers |

## REST

`POST /api/v1/generate` | `POST /api/v1/plan` | `POST /api/v1/plan/render`
`GET /api/v1/jobs` | `GET /api/v1/jobs/{id}` | `GET /api/v1/jobs/{id}/download`
`GET /api/v1/providers` | `GET /health`

## Provider Plugin System

Each provider is one file with one decorator. Adding Gemini takes 40 lines. No router rewrite needed.

```
providers/
  llm_openai.py    @register_llm("openai")
  llm_ollama.py    @register_llm("ollama")
  llm_qwen.py      @register_llm("qwen")
  stock_pexels.py   @register_stock("pexels")
  stock_cogvideo.py @register_stock("cogvideo")
  tts_edge.py       @register_tts("edge-tts")
  tts_cosyvoice.py  @register_tts("cosyvoice")
```

## Videographer Rules Engine

Not just concatenation. Professional editing patterns, codified:

- **Hook**: First 3 seconds grab attention (separate scene, close shot)
- **Pacing**: Scene duration clamped by video type (tutorials: 5-30s, docs: 6-40s)
- **B-roll**: Inserted after 3 consecutive A-roll segments (visual breathing room)
- **Transitions**: Cut for continuity, crossfade for topic change, fade-to-black for outro
- **Rebalancing**: Scene durations scaled to hit target total length

## Dev

```bash
just test      # 42 tests
just lint      # ruff
just typecheck # pyright
just check     # all three
```

## License

MIT
