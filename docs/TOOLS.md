# MCP tools & REST API — ittybitty

Base URL (local): **http://127.0.0.1:11054**

OpenAPI: `/docs` · MCP stream: `/mcp` · Tool catalog: `/api/v1/tools`

---

## MCP tools (16)

Canonical list lives in `videogen_mcp.mcp_registry.MCP_TOOL_CATALOG` — mirrored by `/api/v1/tools` and `/health` `tool_count`.

| Tool | Kind | Description |
|------|------|-------------|
| `videogen_help` | catalog | **Start here** — tools, workflow hints, pack overview |
| `videogen_generate` | pipeline | Short video (~15–50 s) from topic or script |
| `videogen_status` | pipeline | Poll job by ID |
| `videogen_list_jobs` | pipeline | Recent jobs (limit 1–50) |
| `videogen_plan` | pipeline | Mid-length storyboard only (no render) |
| `videogen_plan_render` | pipeline | Plan + render mid-length (3–15 min) |
| `videogen_review` | pipeline | Screening Room VLM critique (`VIDEOGEN_VLM_*`) |
| `videogen_providers` | catalog | LLM / stock / TTS / talker providers |
| `videogen_structures` | catalog | R10 trope / structure YAML presets |
| `videogen_intros` | catalog | Intro sequence packs |
| `videogen_credits` | catalog | End-credits contributor packs |
| `videogen_visual_look` | catalog | AI footage style / material / tone presets |
| `videogen_intro_sample` | catalog | Sample intro prompt block (`intro:id` or bare id) |
| `videogen_credits_sample` | catalog | Sample absurd credits roll |
| `videogen_depot` | depot | List finished videos in depot |
| `videogen_publish_pack` | depot | Publish helpers for a completed job |

### Agent workflow

```
videogen_help()
videogen_generate(topic=…, paragraph_count=3, structure= trope:…, intro= intro:…)
  → videogen_status(job_id)
  → videogen_depot / videogen_publish_pack / videogen_review
```

Mid-length: `videogen_plan` → `videogen_plan_render` → `videogen_status`.

Generate/plan/plan_render accept `visual_style`, `visual_material`, `visual_tone` (see `videogen_visual_look`).

Requires FastMCP (`pip install -e .`). If FastMCP is missing, REST still works; `/mcp` is not mounted and `tool_count` is 0.

---

## REST — generation

### POST `/api/v1/generate`

Short pipeline. Body matches `GenerateRequest` (topic, script, aspect, `paragraph_count`, `structure`, `intro`, visual look, …).

Response: `{ "success": true, "job_id": "...", "status": "queued" }`

### POST `/api/v1/plan` / `/api/v1/plan/render`

Mid-length planning and full render. See OpenAPI schemas.

---

## REST — director packs

| Method | Path | MCP equivalent |
|--------|------|----------------|
| GET | `/api/v1/structures` | `videogen_structures` |
| GET | `/api/v1/intros/packs` | `videogen_intros` |
| GET | `/api/v1/intros/sample` | `videogen_intro_sample` |
| GET | `/api/v1/credits/packs` | `videogen_credits` |
| GET | `/api/v1/credits/sample` | `videogen_credits_sample` |
| GET | `/api/v1/visual-look/catalog` | `videogen_visual_look` |

---

## REST — depot

| Method | Path | MCP equivalent |
|--------|------|----------------|
| GET | `/api/v1/depot` | `videogen_depot` |
| GET | `/api/v1/jobs/{job_id}/publish-pack` | `videogen_publish_pack` |
| POST | `/api/v1/depot/scan` | — |
| DELETE | `/api/v1/depot/{job_id}` | — |

---

## REST — settings

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/settings` | Current config (keys masked) |
| PUT | `/api/v1/settings` | Update and persist `.env` |
| GET | `/api/v1/settings/stock` | Stock provider probes |

Settings remain REST-only (no MCP write surface).

---

## Job lifecycle

```
queued → scripting → fetching_footage → tts → composing → completed
                                                      ↘ failed
```

---

## Example: curl smoke test

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:11054/health
Invoke-RestMethod -Uri http://127.0.0.1:11054/api/v1/tools
```

---

## Authentication

Local dev: no auth on REST/MCP. Do not expose port 11054 to the public internet without a reverse proxy and auth layer.
