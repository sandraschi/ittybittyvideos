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

    pexels_api_key: str = ""

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


@lru_cache
def get_settings() -> Settings:
    return Settings()
