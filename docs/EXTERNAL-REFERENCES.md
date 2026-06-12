# External references — official homepages & repos

Curated links for every provider and dependency ittybitty integrates with. The webapp **Help → Links** tab mirrors this list.

---

## Core stack

| Tool | Homepage | Docs | Repository |
|------|----------|------|------------|
| **ittybitty** | — | [docs/PROVIDERS-AND-MODELS.md](./PROVIDERS-AND-MODELS.md) | [github.com/sandraschi/ittybittyvideos](https://github.com/sandraschi/ittybittyvideos) |
| **FastMCP** | [gofastmcp.com](https://gofastmcp.com/) | [FastMCP docs](https://gofastmcp.com/) | [jlowin/fastmcp](https://github.com/jlowin/fastmcp) |
| **FFmpeg** | [ffmpeg.org](https://ffmpeg.org/) | [Documentation](https://ffmpeg.org/documentation.html) | [FFmpeg/FFmpeg](https://github.com/FFmpeg/FFmpeg) |
| **Python** | [python.org](https://www.python.org/) | — | Requires **3.11+** |

---

## LLM providers (script / planner)

| Key | Get started | API docs | Upstream |
|-----|-------------|----------|----------|
| `deepseek` | [platform.deepseek.com](https://platform.deepseek.com/) | [api-docs.deepseek.com](https://api-docs.deepseek.com/) | [deepseek-ai](https://github.com/deepseek-ai) |
| `openai` | [platform.openai.com](https://platform.openai.com/) | [API reference](https://platform.openai.com/docs/api-reference) | [openai-python](https://github.com/openai/openai-python) |
| `ollama` | [ollama.com](https://ollama.com/) | [docs.ollama.com/api](https://docs.ollama.com/api) | [ollama/ollama](https://github.com/ollama/ollama) |
| `lmstudio` | [lmstudio.ai](https://lmstudio.ai/) | [LM Studio docs](https://lmstudio.ai/docs) | Desktop app + local OpenAI server |
| `qwen` | [DashScope](https://www.alibabacloud.com/product/dashscope) | [Aliyun DashScope help](https://help.aliyun.com/zh/dashscope/) | [QwenLM/Qwen](https://github.com/QwenLM/Qwen) |

---

## Stock footage providers

| Key | Sign up / homepage | API / docs | Notes |
|-----|-------------------|------------|-------|
| `pexels` | [pexels.com](https://www.pexels.com/) | [API documentation](https://www.pexels.com/api/documentation/) · [Get API key](https://www.pexels.com/api/new/) | Free; default provider |
| `veo` | [Google AI Studio](https://aistudio.google.com/) | [Veo in Gemini API](https://ai.google.dev/gemini-api/docs/video) | Cloud AI clips |
| `veo` (Vertex) | [Google Cloud](https://cloud.google.com/) | [Vertex video generation](https://cloud.google.com/vertex-ai/generative-ai/docs/video/generate-videos-from-text) | `GOOGLE_CLOUD_PROJECT` path |
| `omni` | Same as Veo | [Gemini API](https://ai.google.dev/gemini-api/docs) | Multimodal / Omni models |
| Bridge | — | — | Fleet [google-ai-mcp](https://github.com/sandraschi/google-ai-mcp) at `GOOGLE_AI_MCP_URL` |
| `localgen` | — | [Hugging Face Diffusers](https://huggingface.co/docs/diffusers) | [Wan-Video/Wan2.2](https://github.com/Wan-Video/Wan2.2) on local GPU |
| `jellyfin` | [jellyfin.org](https://jellyfin.org/) | [Jellyfin API](https://api.jellyfin.org/) | [jellyfin/jellyfin](https://github.com/jellyfin/jellyfin) |
| `plex` | [plex.tv](https://www.plex.tv/) | [Plex developer](https://developer.plex.tv/) | Home library clips |

Pexels rate limits (default tier): ~200 requests/hour, 20,000/month — see [Pexels API docs](https://www.pexels.com/api/documentation/).

---

## Text-to-speech

| Key | Repository | Homepage / PyPI |
|-----|------------|-----------------|
| `edge-tts` | [rany2/edge-tts](https://github.com/rany2/edge-tts) | [PyPI edge-tts](https://pypi.org/project/edge-tts/) — uses Microsoft Edge online voices, **no API key** |
| `cosyvoice` | [FunAudioLLM/CosyVoice](https://github.com/FunAudioLLM/CosyVoice) | [CosyVoice 3 project page](https://funaudiollm.github.io/cosyvoice3/) |

---

## R1 — forced alignment & karaoke

| Component | Link | Install |
|-----------|------|---------|
| **faster-whisper** | [SYSTRAN/faster-whisper](https://github.com/SYSTRAN/faster-whisper) · [PyPI](https://pypi.org/project/faster-whisper/) | `pip install -e ".[align]"` |
| Original Whisper | [openai/whisper](https://github.com/openai/whisper) | Reference model only |

Word-level ASS subtitles: `VIDEOGEN_SUB_STYLE=karaoke`.

---

## R2 — beat snap & music ducking

| Component | Link | Install |
|-----------|------|---------|
| **librosa** | [librosa.org](https://librosa.org/) · [librosa/librosa](https://github.com/librosa/librosa) | `pip install -e ".[beats]"` |

Snaps scene cuts to BGM beats when `bgm_url` is set; FFmpeg sidechain ducking under narration.

---

## R3 — Screening Room (VLM)

| Component | Link | Config |
|-----------|------|--------|
| Ollama vision models | [ollama.com/search?c=vision](https://ollama.com/search?c=vision) | `VIDEOGEN_VLM_URL=http://localhost:11434/v1` |
| Qwen-VL | [QwenLM/Qwen-VL](https://github.com/QwenLM/Qwen-VL) | e.g. `VIDEOGEN_VLM_MODEL=qwen3.5-vl` |

MCP tool: `videogen_review`. Mid-length jobs write `critique_pass_*.json` in the job work directory.

---

## R9 — talking-head PiP overlay

ittybitty expects an **external HTTP service** (models not bundled):

```
POST {TALKER_URL}/generate
  multipart: audio=<wav/mp3>, image=<png/jpg>
  → 200 video/mp4
```

Default `TALKER_URL`: `http://localhost:11100`.

| Backend | Repository | Project page |
|---------|------------|--------------|
| **SadTalker** | [OpenTalker/SadTalker](https://github.com/OpenTalker/SadTalker) | [sadtalker.github.io](https://sadtalker.github.io/) |
| **LivePortrait** | [KlingTeam/LivePortrait](https://github.com/KlingTeam/LivePortrait) | [liveportrait.github.io](https://liveportrait.github.io/) |
| **EchoMimic** | [antgroup/echomimic](https://github.com/antgroup/echomimic) | [antgroup.github.io/ai/echomimic](https://antgroup.github.io/ai/echomimic/) |

Hugging Face demo: [vinthony/SadTalker](https://huggingface.co/spaces/vinthony/SadTalker).

---

## MCP & REST (ittybitty)

| Surface | URL |
|---------|-----|
| Health | `http://127.0.0.1:11054/health` |
| OpenAPI | `http://127.0.0.1:11054/docs` |
| MCP (HTTP) | `http://127.0.0.1:11054/mcp` |
| Dev UI (Vite) | `http://127.0.0.1:11055` |

See [TOOLS.md](./TOOLS.md) for all seven MCP tools.

---

## Fleet local video generators (Windows paths)

See **[LOCAL-VIDEO-GENERATORS.md](./LOCAL-VIDEO-GENERATORS.md)** for the full integration matrix.

| Fleet path | Status | Links |
|------------|--------|-------|
| *(built-in)* `videogen-mcp/localgen_server` | **Integrated** as `localgen` on `:8188` | [Wan 2.2 Diffusers](https://huggingface.co/Wan-AI/Wan2.2-T2V-A14B-Diffusers) |
| `D:\Dev\repos\externals\wan-video` | **Not wired** — native Wan suite | [Wan-Video/Wan2.2](https://github.com/Wan-Video/Wan2.2) |
| `D:\Dev\repos\externals\hunyuan-worldplay` | **Roadmap** — WorldPlay worlds | [HY-World project](https://3d-models.hunyuan.tencent.com/world/) · [HF HY-WorldPlay](https://huggingface.co/tencent/HY-WorldPlay) · [arXiv](https://arxiv.org/abs/2512.14614) |

---

## Related fleet MCP servers

| Server | Repo | Used for |
|--------|------|----------|
| jellyfin-mcp | Fleet | Same Jellyfin URL/key as stock `jellyfin` |
| plex-mcp / PlexOps | Fleet | Same Plex token as stock `plex` |
| google-ai-mcp | [sandraschi/google-ai-mcp](https://github.com/sandraschi/google-ai-mcp) | Veo/Omni stock bridge |

---

## Internal docs index

| Doc | Purpose |
|-----|---------|
| [PROVIDERS-AND-MODELS.md](./PROVIDERS-AND-MODELS.md) | Registry keys, env vars, MCP tools |
| [CONFIGURATION.md](./CONFIGURATION.md) | `.env` reference |
| [TOOLS.md](./TOOLS.md) | REST + MCP API |
| [E2E.md](./E2E.md) | Playwright smoke tests |
| [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) | Common failures |
