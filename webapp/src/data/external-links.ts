/** Official homepages and repos for providers / tools (Help + docs). */

export type ExternalRef = {
  name: string;
  homepage?: string;
  docs?: string;
  repo?: string;
  api?: string;
  note?: string;
};

export const CORE_STACK: ExternalRef[] = [
  {
    name: "ittybitty (this repo)",
    repo: "https://github.com/sandraschi/ittybittyvideos",
    note: "Private fleet repo; product name ittybitty, package videogen-mcp",
  },
  { name: "FastMCP", homepage: "https://gofastmcp.com/", repo: "https://github.com/jlowin/fastmcp" },
  { name: "FFmpeg", homepage: "https://ffmpeg.org/", docs: "https://ffmpeg.org/documentation.html" },
  { name: "Python", homepage: "https://www.python.org/", note: "Requires 3.11+" },
];

export const LLM_PROVIDERS: ExternalRef[] = [
  {
    name: "DeepSeek API",
    homepage: "https://platform.deepseek.com/",
    docs: "https://api-docs.deepseek.com/",
    repo: "https://github.com/deepseek-ai",
    note: "OpenAI-compatible; default cloud option in Generate UI",
  },
  {
    name: "OpenAI",
    homepage: "https://platform.openai.com/",
    docs: "https://platform.openai.com/docs/api-reference",
    repo: "https://github.com/openai/openai-python",
  },
  {
    name: "Ollama",
    homepage: "https://ollama.com/",
    docs: "https://docs.ollama.com/api",
    repo: "https://github.com/ollama/ollama",
    api: "http://127.0.0.1:11434",
    note: "Local LLM + vision models for R3 screening",
  },
  {
    name: "LM Studio",
    homepage: "https://lmstudio.ai/",
    docs: "https://lmstudio.ai/docs",
    note: "OpenAI-compatible local server (default port 1234)",
  },
  {
    name: "Qwen / DashScope",
    homepage: "https://www.alibabacloud.com/product/dashscope",
    docs: "https://help.aliyun.com/zh/dashscope/",
    repo: "https://github.com/QwenLM/Qwen",
  },
];

export const STOCK_PROVIDERS: ExternalRef[] = [
  {
    name: "Pexels",
    homepage: "https://www.pexels.com/",
    docs: "https://www.pexels.com/api/documentation/",
    api: "https://www.pexels.com/api/new/",
    note: "Free API key; default stock provider",
  },
  {
    name: "Google Veo (Gemini API)",
    docs: "https://ai.google.dev/gemini-api/docs/video",
    homepage: "https://ai.google.dev/",
    note: "Text-to-video; stock provider veo",
  },
  {
    name: "Google Veo (Vertex AI)",
    docs: "https://cloud.google.com/vertex-ai/generative-ai/docs/video/generate-videos-from-text",
    homepage: "https://cloud.google.com/vertex-ai",
    note: "Enterprise / GCP project path",
  },
  {
    name: "google-ai-mcp (fleet bridge)",
    repo: "https://github.com/sandraschi/google-ai-mcp",
    note: "Recommended bridge at GOOGLE_AI_MCP_URL (e.g. :11014)",
  },
  {
    name: "Jellyfin",
    homepage: "https://jellyfin.org/",
    docs: "https://api.jellyfin.org/",
    repo: "https://github.com/jellyfin/jellyfin",
    note: "Stock provider jellyfin — your home library",
  },
  {
    name: "Plex",
    homepage: "https://www.plex.tv/",
    docs: "https://developer.plex.tv/",
    note: "Stock provider plex — same token as plex-mcp",
  },
  {
    name: "Wan 2.2 (LocalGen)",
    repo: "https://github.com/Wan-Video/Wan2.2",
    docs: "https://huggingface.co/Wan-AI",
    note: "Built-in sidecar :8188; fleet clone: D:\\Dev\\repos\\externals\\wan-video",
  },
  {
    name: "Hugging Face Diffusers",
    homepage: "https://huggingface.co/docs/diffusers",
    repo: "https://github.com/huggingface/diffusers",
    note: "LocalGen / cogvideo extra",
  },
];

export const TTS_PROVIDERS: ExternalRef[] = [
  {
    name: "edge-tts",
    repo: "https://github.com/rany2/edge-tts",
    homepage: "https://pypi.org/project/edge-tts/",
    note: "Microsoft Edge online TTS — no API key",
  },
  {
    name: "CosyVoice",
    repo: "https://github.com/FunAudioLLM/CosyVoice",
    homepage: "https://funaudiollm.github.io/cosyvoice3/",
    note: "Local zero-shot TTS server (COSYVOICE_URL)",
  },
];

export const FEATURE_STACK: ExternalRef[] = [
  {
    name: "faster-whisper (R1 align)",
    repo: "https://github.com/SYSTRAN/faster-whisper",
    homepage: "https://pypi.org/project/faster-whisper/",
    note: "pip install -e \".[align]\"",
  },
  {
    name: "OpenAI Whisper",
    repo: "https://github.com/openai/whisper",
    note: "Original model; faster-whisper is the runtime ittybitty uses",
  },
  {
    name: "librosa (R2 beats)",
    homepage: "https://librosa.org/",
    repo: "https://github.com/librosa/librosa",
    note: "pip install -e \".[beats]\"",
  },
  {
    name: "SadTalker (R9 talker)",
    repo: "https://github.com/OpenTalker/SadTalker",
    homepage: "https://sadtalker.github.io/",
    note: "Wrap behind TALKER_URL POST /generate",
  },
  {
    name: "LivePortrait",
    repo: "https://github.com/KlingTeam/LivePortrait",
    homepage: "https://liveportrait.github.io/",
    note: "Alternative talker backend; animal mode for pets",
  },
  {
    name: "EchoMimic",
    repo: "https://github.com/antgroup/echomimic",
    homepage: "https://antgroup.github.io/ai/echomimic/",
    note: "Audio-driven portrait; same HTTP contract possible",
  },
];

export const VLM_SCREENING: ExternalRef[] = [
  {
    name: "Ollama vision models",
    docs: "https://ollama.com/search?c=vision",
    note: "qwen3.5-vl, gemma, llava — VIDEOGEN_VLM_URL",
  },
  {
    name: "Qwen-VL",
    repo: "https://github.com/QwenLM/Qwen-VL",
    note: "Common choice for local screening",
  },
];

export const FLEET_LOCAL_GENERATORS: ExternalRef[] = [
  {
    name: "LocalGen (built into ittybitty)",
    note: "Integrated: VIDEOGEN_STOCK_PROVIDER=localgen · http://127.0.0.1:8188 · see repo docs/LOCAL-VIDEO-GENERATORS.md",
  },
  {
    name: "wan-video (fleet external)",
    homepage: "https://github.com/Wan-Video/Wan2.2",
    note: "Fleet path: D:\\Dev\\repos\\externals\\wan-video — native Wan (S2V, Animate); not wired to LocalGen HTTP yet",
  },
  {
    name: "hunyuan-worldplay (fleet external)",
    homepage: "https://3d-models.hunyuan.tencent.com/world/",
    docs: "https://huggingface.co/tencent/HY-WorldPlay",
    repo: "https://arxiv.org/abs/2512.14614",
    note: "Fleet path: D:\\Dev\\repos\\externals\\hunyuan-worldplay — interactive worlds; roadmap",
  },
];

export const ALL_GROUPS: { title: string; items: ExternalRef[] }[] = [
  { title: "Core stack", items: CORE_STACK },
  { title: "LLM providers", items: LLM_PROVIDERS },
  { title: "Stock footage", items: STOCK_PROVIDERS },
  { title: "Fleet local video generators", items: FLEET_LOCAL_GENERATORS },
  { title: "Text-to-speech", items: TTS_PROVIDERS },
  { title: "R1 / R2 / R9 features", items: FEATURE_STACK },
  { title: "R3 vision / screening", items: VLM_SCREENING },
];
