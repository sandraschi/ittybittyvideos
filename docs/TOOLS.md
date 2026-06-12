# MCP tools & REST API — ittybitty

Base URL (local): **http://127.0.0.1:11054**

OpenAPI: `/docs` · MCP stream: `/mcp`

---

## MCP tools

| Tool | Description |
|------|-------------|
| `videogen_generate` | Short video (30–60 s) from topic or script |
| `videogen_plan` | Mid-length storyboard only (no render) |
| `videogen_plan_render` | Plan + render mid-length (3–15 min) |
| `videogen_status` | Poll job by ID |
| `videogen_list_jobs` | Recent jobs (limit 1–50) |
| `videogen_providers` | List LLM / stock / TTS providers |

Requires FastMCP installed (`pip install -e .` includes it). If FastMCP is missing, REST still works; `/mcp` is not mounted.

---

## REST — generation

### POST `/api/v1/generate`

Short pipeline. Body (JSON):

```json
{
  "topic": "Vienna coffee houses",
  "mode": "deepseek",
  "aspect": "9:16",
  "duration": 45
}
```

Or custom script:

```json
{
  "script": "Your narration paragraphs...",
  "mode": "script"
}
```

Response: `{ "job_id": "...", "status": "queued" }`

### GET `/api/v1/status/{job_id}`

Progress, paths, errors.

### POST `/api/v1/plan` / `/api/v1/plan-render`

Mid-length planning and full render. See OpenAPI schemas.

---

## REST — depot

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/depot` | List persisted jobs |
| POST | `/api/v1/depot/scan` | Rescan `output/` into SQLite |
| DELETE | `/api/v1/depot/{job_id}` | Remove DB row + optional files |
| GET | `/api/v1/depot/{job_id}/poster` | Thumbnail JPEG |
| GET | `/api/v1/download/{filename}` | Download MP4 (safe path resolve) |

---

## REST — settings

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/settings` | Current config (keys masked) |
| PUT | `/api/v1/settings` | Update and persist `.env` |
| GET | `/api/v1/settings/health` | LLM + stock provider probes |

---

## REST — publish

Helpers for manual upload workflows (opens platform URLs, copy hashtags).

---

## Job lifecycle

```
queued → scripting → fetching_footage → tts → composing → completed
                                                      ↘ failed
```

State is stored in SQLite (`depot.db`) and mirrored in API responses. Completed jobs appear in **Depot** with file path, duration, and poster frame.

---

## Example: curl smoke test

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:11054/health
```

```powershell
$body = @{ topic = "sunset"; mode = "script"; script = "The sun sets slowly." } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:11054/api/v1/generate -Body $body -ContentType "application/json"
```

---

## Authentication

Local dev: no auth on REST/MCP. Do not expose port 11054 to the public internet without adding a reverse proxy and auth layer.
