from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"env_prefix": "", "env_file": ".env", "extra": "ignore"}

    videogen_llm_provider: str = "openai"
    videogen_stock_provider: str = "pexels"
    videogen_tts_provider: str = "edge-tts"

    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o-mini"

    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-v4-flash"

    lmstudio_base_url: str = "http://localhost:1234/v1"
    lmstudio_api_key: str = "lm-studio"
    lmstudio_model: str = ""

    ollama_base_url: str = "http://localhost:11434/v1"
    ollama_model: str = "llama3.2:3b"

    pexels_api_key: str = ""
    pixabay_api_key: str = ""
    coverr_api_key: str = ""
    nasa_api_key: str = ""

    cogvideo_url: str = "http://localhost:8188"
    localgen_url: str = ""

    google_api_key: str = ""
    google_cloud_project: str = ""
    google_cloud_location: str = "us-central1"
    google_ai_mcp_url: str = ""
    google_veo_model: str = "veo-3.1-preview-002"
    google_omni_model: str = "gemini-omni-flash"

    jellyfin_server_url: str = ""
    jellyfin_url: str = ""
    jellyfin_api_key: str = ""
    plex_url: str = ""
    plex_server_url: str = ""
    plex_token: str = ""

    edge_tts_voice: str = "en-US-AriaNeural"

    videogen_output_dir: Path = Path("./output")
    videogen_cache_dir: Path = Path("./cache")

    videogen_port: int = 11054
    videogen_host: str = "127.0.0.1"

    videogen_default_aspect: str = "9:16"
    videogen_default_fps: int = 30
    videogen_clip_duration: float = 5.0
    videogen_paragraph_count: int = 3

    # R1: subtitle alignment + styling
    videogen_align: bool = True  # run faster-whisper alignment when provider lacks word timestamps
    videogen_sub_style: str = "sentence"  # sentence | karaoke
    videogen_whisper_model: str = "small"
    videogen_whisper_device: str = "auto"  # auto | cuda | cpu

    # R2: beat-aware cuts + music ducking
    videogen_beat_snap: bool = True  # snap scene cuts to bgm beats (needs `beats` extra)
    videogen_beat_tolerance: float = 0.4  # max seconds a cut may move to reach a beat
    videogen_duck: bool = True  # sidechain-compress bgm under narration
    videogen_duck_ratio: float = 8.0  # sidechaincompress ratio (NOT dB; ffmpeg has no dB knob)
    videogen_bgm_volume: float = 0.3  # bgm pre-duck gain

    # R9: talking-head overlay (FOSS backends via HTTP, e.g. SadTalker/EchoMimic wrapper)
    videogen_talker_provider: str = ""  # empty = off | sadtalker
    talker_url: str = "http://localhost:11100"
    videogen_talker_source: str = ""  # path to source face image (photo, anime girl render, or one good Benny pic)
    videogen_talker_corner: str = "bottom-right"  # bottom-right | bottom-left | top-right | top-left
    videogen_talker_scale: float = 0.28  # head height as fraction of video height

    # R3: Screening Room (closed-loop VLM self-critique on mid-length renders)
    videogen_screening_passes: int = 1  # 0 = off; skipped with a warning when VLM unreachable
    videogen_vlm_url: str = "http://localhost:11434/v1"  # OpenAI-compatible vision endpoint (Ollama default)
    videogen_vlm_model: str = "qwen3.5-vl"


@lru_cache
def get_settings() -> Settings:
    return Settings()
