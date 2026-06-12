# Providers, models, and MCP tools — ittybitty

Canonical reference for everything pluggable in `videogen_mcp.providers`. Settings keys live in [CONFIGURATION.md](./CONFIGURATION.md); REST/MCP surface in [TOOLS.md](./TOOLS.md).

**Official homepages & GitHub repos:** [EXTERNAL-REFERENCES.md](./EXTERNAL-REFERENCES.md) (also in webapp **Help → Links**).
---

## Registry overview

| Kind | Registry keys | Default (`settings.py`) |
|------|---------------|-------------------------|
| LLM | `deepseek`, `openai`, `ollama`, `lmstudio`, `qwen` | `videogen_llm_provider=openai` |
| Stock | `pexels`, `veo`, `omni`, `localgen`, `cogvideo`* , `jellyfin`, `plex` | `videogen_stock_provider=pexels` |
| TTS | `edge-tts`, `cosyvoice` | `videogen_tts_provider=edge-tts` |
| Talker | `sadtalker` | `videogen_talker_provider=` (empty = off) |

\* `cogvideo` is an alias for `localgen` (backward compatibility).

Discover at runtime: `GET /api/v1/providers` or MCP `videogen_providers()`.

---

## LLM providers (script / storyboard text)

Used for **topic → narration** on short jobs and **chapter planning** on mid-length jobs. Custom script mode skips LLM entirely.

| Key | Module | Primary env vars | Default model | Official links |
|-----|--------|------------------|---------------|----------------|
| `deepseek` | `llm_deepseek.py` | `DEEPSEEK_API_KEY`, `DEEPSEEK_BASE_URL`, `DEEPSEEK_MODEL` | `deepseek-chat` | [Platform](https://platform.deepseek.com/) · [API docs](https://api-docs.deepseek.com/) |
| `openai` | `llm_openai.py` | `OPENAI_API_KEY`, `OPENAI_BASE_URL`, `OPENAI_MODEL` | `gpt-4o-mini` | [Platform](https://platform.openai.com/) |
| `ollama` | `llm_ollama.py` | `OLLAMA_BASE_URL`, `OLLAMA_MODEL` | `llama3.2` | [ollama.com](https://ollama.com/) · [API](https://docs.ollama.com/api) |
| `lmstudio` | `llm_lmstudio.py` | `LMSTUDIO_BASE_URL`, `LMSTUDIO_MODEL` | (from server) | [lmstudio.ai](https://lmstudio.ai/) |
| `qwen` | `llm_qwen.py` | `QWEN_API_KEY`, `QWEN_BASE_URL`, `QWEN_MODEL` | `qwen-plus` | [DashScope](https://help.aliyun.com/zh/dashscope/) |
**Mid-length planner** (`services/planner.py`) uses `VIDEOGEN_LLM_PROVIDER` and the matching model env — not a hardcoded OpenAI path (Fable fix, uncommitted WIP).

**Topic routing** (`providers/llm_resolve.py`): short pipeline can pick provider by topic keywords when multiple keys are configured.

Model lists for Settings UI: `GET /api/v1/settings/models` (probes Ollama/LM Studio when reachable).

---

## Stock footage providers

Each scene gets a search query (from LLM or storyboard). Provider downloads or generates a clip, cached under `VIDEOGEN_CACHE_DIR`.

| Key | Module | Env vars | Links |
|-----|--------|----------|-------|
| `pexels` | `stock_pexels.py` | `PEXELS_API_KEY` | [API docs](https://www.pexels.com/api/documentation/) · [Get key](https://www.pexels.com/api/new/) |
| `veo` | `stock_google.py` | `GOOGLE_AI_MCP_URL` or GCP keys, `GOOGLE_VEO_MODEL` | [Gemini API video](https://ai.google.dev/gemini-api/docs/video) |
| `omni` | `stock_google.py` | Same bridge or direct keys, `GOOGLE_OMNI_MODEL` | [Google AI](https://ai.google.dev/) |
| `localgen` | `stock_localgen.py` | `LOCALGEN_URL`, `LOCALGEN_BACKEND` | [Wan 2.2](https://github.com/Wan-Video/Wan2.2) · [Diffusers](https://huggingface.co/docs/diffusers) |
| `jellyfin` | `stock_library.py` | `JELLYFIN_URL`, `JELLYFIN_API_KEY` | [jellyfin.org](https://jellyfin.org/) · [API](https://api.jellyfin.org/) |
| `plex` | `stock_library.py` | `PLEX_URL`, `PLEX_TOKEN` | [developer.plex.tv](https://developer.plex.tv/) |
Library providers use `library://` URLs in the cache layer; clips are ffmpeg-trimmed from existing media.

---

## TTS providers

| Key | Module | Env vars | Links |
|-----|--------|----------|-------|
| `edge-tts` | `tts_edge.py` | (none) | [rany2/edge-tts](https://github.com/rany2/edge-tts) |
| `cosyvoice` | `tts_cosyvoice.py` | `COSYVOICE_URL` | [FunAudioLLM/CosyVoice](https://github.com/FunAudioLLM/CosyVoice) |
When `VIDEOGEN_ALIGN=true` and the `align` extra is installed, **faster-whisper** refines word timing for karaoke ASS (`VIDEOGEN_SUB_STYLE=karaoke`).

---

## Talker providers (R9 — PiP overlay)

Optional post-pass on **short pipeline** only. Requires source face image + external render service.

| Key | Module | Env vars | Upstream |
|-----|--------|----------|----------|
| `sadtalker` | `talker_sadtalker.py` | `VIDEOGEN_TALKER_PROVIDER`, `TALKER_URL`, `VIDEOGEN_TALKER_SOURCE`, … | [OpenTalker/SadTalker](https://github.com/OpenTalker/SadTalker) · [LivePortrait](https://github.com/KlingTeam/LivePortrait) · [EchoMimic](https://github.com/antgroup/echomimic) |
Default `TALKER_URL`: `http://localhost:11100`. Pipeline logs and continues without overlay if the backend is down.

Compatible backends: SadTalker, EchoMimic, Hallo2, LivePortrait (including pet/animal modes) behind the same HTTP contract.

---

## Vision / screening (R3 — not a provider registry entry)

Screening Room uses OpenAI-compatible **chat completions with vision**:

| Setting | Default | Purpose |
|---------|---------|---------|
| `VIDEOGEN_VLM_URL` | `http://localhost:11434/v1` | Ollama or other OpenAI shim |
| `VIDEOGEN_VLM_MODEL` | `qwen3.5-vl` | Must support image inputs |
| `VIDEOGEN_SCREENING_PASSES` | `1` | `0` disables; skipped with warning if VLM unreachable |

Mid-length `plan_render` runs critique passes after compose; writes `critique_pass_*.json` in the job work dir. MCP `videogen_review` critiques any completed depot job.

---

## Audio / alignment extras (R1 + R2)

Not separate providers — pipeline features controlled by env:

| Feature | Extra (`pip install -e ".[…]"`) | Key settings |
|---------|-----------------------------------|--------------|
| R1 forced alignment | `align` | `VIDEOGEN_ALIGN`, `VIDEOGEN_WHISPER_MODEL`, `VIDEOGEN_WHISPER_DEVICE`, `VIDEOGEN_SUB_STYLE` |
| R2 beat snap + duck | `beats` | `VIDEOGEN_BEAT_SNAP`, `VIDEOGEN_BEAT_TOLERANCE`, `VIDEOGEN_DUCK`, `VIDEOGEN_DUCK_RATIO`, `VIDEOGEN_BGM_VOLUME` |

---

## MCP tools (7)

| Tool | Pipeline |
|------|----------|
| `videogen_generate` | Short (30–60 s) |
| `videogen_plan` | Mid storyboard only |
| `videogen_plan_render` | Mid plan + render + optional R3 screening |
| `videogen_status` | Poll job |
| `videogen_list_jobs` | Recent jobs |
| `videogen_providers` | Registry listing |
| `videogen_review` | R3 VLM critique on finished MP4 |

REST mirrors generation, depot, settings, publish, logs, and `/api/v1/tools`.

---

## SPEC roadmap vs shipped

| Phase | Status |
|-------|--------|
| R1 Alignment / karaoke | Done |
| R2 Beat snap + ducking | Done (wired in `pipeline.py`) |
| R3 Screening Room | Done (needs live VLM validation) |
| R9 Talking head | Plumbing done (needs external `TALKER_URL` backend) |
| R4–R8 | Not started |

See [SPEC.md](../SPEC.md) for R4+ definitions.
