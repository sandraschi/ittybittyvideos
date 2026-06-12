# videogen-mcp — AI Video Generation MCP Server

**Version**: 0.1.0
**Port**: 11054 (backend) / 11055 (frontend)
**Status**: MVP

## Problem

MoneyPrinterTurbo proved the market (86k stars): topic in → short video out.
But it ships with zero tests, a monolith LLM router, bundled proprietary fonts,
TOML-only config, and no MCP integration. We build the fleet-grade version.

## Architecture

```
Topic/Keyword
     │
     ▼
┌─────────────────────────────────────────────────┐
│  videogen-mcp (FastMCP 3.2, port 11054)         │
│                                                  │
│  Pipeline:                                       │
│  1. LLM Provider → script + search terms         │
│  2. Stock Provider → download footage clips      │
│  3. TTS Provider → narration audio               │
│  4. Subtitle Service → .srt from TTS timestamps  │
│  5. Compose Service → FFmpeg → final .mp4        │
│                                                  │
│  Plugin Registry:                                │
│  ├── LLM: openai, ollama, gemini, deepseek       │
│  ├── Stock: pexels, pixabay, (veo bridge)        │
│  └── TTS: edge-tts, (speech-mcp bridge)          │
└─────────────────────────────────────────────────┘
```

## Provider Plugin System

Each provider implements a base class and registers via entry point or
explicit import. Adding a provider = adding one file. No monolith router.

## MCP Tools

| Tool | Description |
|------|-------------|
| `videogen_generate` | Start video generation from topic/script |
| `videogen_status` | Poll job progress (SSE-friendly) |
| `videogen_list_jobs` | List recent generation jobs |
| `videogen_templates` | List/apply video style templates |
| `videogen_providers` | List available LLM/stock/TTS providers |

## Config

12-factor env vars with `.env` support:

- `VIDEOGEN_LLM_PROVIDER` (default: openai)
- `VIDEOGEN_STOCK_PROVIDER` (default: pexels)
- `VIDEOGEN_TTS_PROVIDER` (default: edge-tts)
- `OPENAI_API_KEY`, `PEXELS_API_KEY`
- `VIDEOGEN_OUTPUT_DIR`, `VIDEOGEN_CACHE_DIR`
- `VIDEOGEN_PORT` (default: 11054)

## Gaps Addressed

See README.md gap analysis table.
