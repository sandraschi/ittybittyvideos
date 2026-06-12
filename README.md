# videogen-mcp

AI-powered short video generation MCP server. Topic in, TikTok-ready video out.

**Port**: 11054 (backend) | **Version**: 0.1.0

## What It Does

```
Topic/Keyword --> LLM Script --> Stock Footage --> TTS Voice --> Subtitles --> FFmpeg --> .mp4
```

## vs MoneyPrinterTurbo

| MoneyPrinterTurbo Gap | videogen-mcp |
|----------------------|--------------|
| Zero tests | 20+ tests from day one |
| Monolith 17-provider LLM file | Plugin registry (one file per provider) |
| TOML-only secrets | 12-factor env vars |
| Bundled proprietary fonts | System fonts + open-source fallbacks |
| Port 8080 | Fleet port 11054 |
| No MCP integration | FastMCP 3.2 (Cursor/Claude callable) |
| Stock footage only | Extensible (Veo AI video bridge ready) |
| Edge TTS only | Plugin TTS (speech-mcp bridge ready) |
| No progress streaming | Job status polling |
| No asset caching | Content-hash dedup cache |
| g4f gray-area dep | Clean provider list only |

## Quick Start

```bash
cp .env.example .env
# Edit .env with your API keys (OPENAI_API_KEY, PEXELS_API_KEY)

just bootstrap
just dev
```

Or without just:

```bash
uv sync
uv run python -m videogen_mcp.server
```

## MCP Tools

| Tool | Description |
|------|-------------|
| `videogen_generate` | Start video generation from topic/script |
| `videogen_status` | Poll job progress |
| `videogen_list_jobs` | List recent jobs |
| `videogen_providers` | List available providers |

## REST API

- `GET /health`
- `POST /api/v1/generate`
- `GET /api/v1/jobs`
- `GET /api/v1/jobs/{id}`
- `GET /api/v1/jobs/{id}/download`
- `GET /api/v1/providers`

## Provider System

Each provider is a single file implementing a base class. Adding a provider = adding one file.

**LLM**: `openai`, `ollama` (extensible: gemini, deepseek)
**Stock**: `pexels` (extensible: pixabay, veo)
**TTS**: `edge-tts` (extensible: speech-mcp bridge)

## Development

```bash
just test      # Run tests
just lint      # Lint check
just typecheck # Type check
just check     # All three
```

## License

MIT
