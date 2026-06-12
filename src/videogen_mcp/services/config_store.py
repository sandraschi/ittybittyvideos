from __future__ import annotations

import os
import re
from pathlib import Path

from pydantic import BaseModel, Field

SECRET_MASK = "••••••••"
_ENV_KEY_PATTERN = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)=(.*)$")

# Order preserved in written .env
ENV_KEYS_ORDER = [
    "VIDEOGEN_LLM_PROVIDER",
    "DEEPSEEK_API_KEY",
    "DEEPSEEK_BASE_URL",
    "DEEPSEEK_MODEL",
    "OPENAI_API_KEY",
    "OPENAI_BASE_URL",
    "OPENAI_MODEL",
    "LMSTUDIO_BASE_URL",
    "LMSTUDIO_API_KEY",
    "LMSTUDIO_MODEL",
    "OLLAMA_BASE_URL",
    "OLLAMA_MODEL",
    "VIDEOGEN_STOCK_PROVIDER",
    "PEXELS_API_KEY",
    "COGVIDEO_URL",
    "LOCALGEN_URL",
    "GOOGLE_API_KEY",
    "GOOGLE_CLOUD_PROJECT",
    "GOOGLE_CLOUD_LOCATION",
    "GOOGLE_AI_MCP_URL",
    "GOOGLE_VEO_MODEL",
    "GOOGLE_OMNI_MODEL",
    "VIDEOGEN_TTS_PROVIDER",
    "EDGE_TTS_VOICE",
    "VIDEOGEN_OUTPUT_DIR",
    "VIDEOGEN_CACHE_DIR",
    "VIDEOGEN_PORT",
    "VIDEOGEN_HOST",
    "VIDEOGEN_ALIGN",
    "VIDEOGEN_SUB_STYLE",
    "VIDEOGEN_WHISPER_MODEL",
    "VIDEOGEN_WHISPER_DEVICE",
]

SECRET_KEYS = frozenset(
    {
        "OPENAI_API_KEY",
        "DEEPSEEK_API_KEY",
        "PEXELS_API_KEY",
        "LMSTUDIO_API_KEY",
        "GOOGLE_API_KEY",
    }
)


class ProviderSettingsPublic(BaseModel):
    id: str
    label: str
    ready: bool = False
    model: str = ""
    base_url: str = ""
    api_key_set: bool = False
    api_key_hint: str = ""


class LlmModelsResponse(BaseModel):
    provider: str
    available: bool
    error: str = ""
    models: list[str] = Field(default_factory=list)
    selected_model: str = ""


class SettingsPublic(BaseModel):
    env_path: str
    videogen_llm_provider: str
    llm_providers: list[ProviderSettingsPublic]
    videogen_stock_provider: str
    pexels_api_key_set: bool
    pexels_api_key_hint: str
    cogvideo_url: str
    cogvideo_ready: bool
    cogvideo_error: str
    google_api_key_set: bool = False
    google_api_key_hint: str = ""
    google_cloud_project: str = ""
    google_ai_mcp_url: str = ""
    veo_ready: bool = False
    omni_ready: bool = False
    stock_ready_for_renders: bool
    stock_hint: str
    videogen_tts_provider: str
    edge_tts_voice: str


class SettingsUpdate(BaseModel):
    videogen_llm_provider: str | None = None
    deepseek_api_key: str | None = None
    deepseek_base_url: str | None = None
    deepseek_model: str | None = None
    openai_api_key: str | None = None
    openai_base_url: str | None = None
    openai_model: str | None = None
    lmstudio_base_url: str | None = None
    lmstudio_api_key: str | None = None
    lmstudio_model: str | None = None
    ollama_base_url: str | None = None
    ollama_model: str | None = None
    pexels_api_key: str | None = None
    cogvideo_url: str | None = None
    google_api_key: str | None = None
    google_cloud_project: str | None = None
    google_cloud_location: str | None = None
    google_ai_mcp_url: str | None = None
    google_veo_model: str | None = None
    google_omni_model: str | None = None
    videogen_stock_provider: str | None = None
    videogen_tts_provider: str | None = None
    edge_tts_voice: str | None = None


def env_file_path() -> Path:
    return Path(os.environ.get("VIDEOGEN_ENV_FILE", ".env")).resolve()


def _hint_secret(value: str) -> str:
    if not value or len(value) < 8:
        return "set" if value else ""
    return f"…{value[-4:]}"


def read_env_map() -> dict[str, str]:
    path = env_file_path()
    if not path.is_file():
        return {}
    result: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        match = _ENV_KEY_PATTERN.match(stripped)
        if match:
            result[match.group(1)] = match.group(2)
    return result


def write_env_map(updates: dict[str, str | None]) -> None:
    """Merge updates into .env; None skips, masked/empty secrets keep existing."""
    path = env_file_path()
    current = read_env_map()

    for key, value in updates.items():
        if value is None:
            continue
        if key in SECRET_KEYS:
            cleaned = (value or "").strip()
            if not cleaned or cleaned == SECRET_MASK:
                continue
        current[key] = str(value)

    lines: list[str] = []
    written: set[str] = set()
    for key in ENV_KEYS_ORDER:
        if key in current:
            lines.append(f"{key}={current[key]}")
            written.add(key)
    for key in sorted(current):
        if key not in written:
            lines.append(f"{key}={current[key]}")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def reload_settings():
    from videogen_mcp.config.settings import get_settings

    get_settings.cache_clear()
    for key, value in read_env_map().items():
        os.environ[key] = value
    return get_settings()


def settings_update_to_env(payload: SettingsUpdate) -> dict[str, str | None]:
    field_map = {
        "videogen_llm_provider": "VIDEOGEN_LLM_PROVIDER",
        "deepseek_api_key": "DEEPSEEK_API_KEY",
        "deepseek_base_url": "DEEPSEEK_BASE_URL",
        "deepseek_model": "DEEPSEEK_MODEL",
        "openai_api_key": "OPENAI_API_KEY",
        "openai_base_url": "OPENAI_BASE_URL",
        "openai_model": "OPENAI_MODEL",
        "lmstudio_base_url": "LMSTUDIO_BASE_URL",
        "lmstudio_api_key": "LMSTUDIO_API_KEY",
        "lmstudio_model": "LMSTUDIO_MODEL",
        "ollama_base_url": "OLLAMA_BASE_URL",
        "ollama_model": "OLLAMA_MODEL",
        "pexels_api_key": "PEXELS_API_KEY",
        "cogvideo_url": "COGVIDEO_URL",
        "google_api_key": "GOOGLE_API_KEY",
        "google_cloud_project": "GOOGLE_CLOUD_PROJECT",
        "google_cloud_location": "GOOGLE_CLOUD_LOCATION",
        "google_ai_mcp_url": "GOOGLE_AI_MCP_URL",
        "google_veo_model": "GOOGLE_VEO_MODEL",
        "google_omni_model": "GOOGLE_OMNI_MODEL",
        "videogen_stock_provider": "VIDEOGEN_STOCK_PROVIDER",
        "videogen_tts_provider": "VIDEOGEN_TTS_PROVIDER",
        "edge_tts_voice": "EDGE_TTS_VOICE",
    }
    out: dict[str, str | None] = {}
    for field, env_key in field_map.items():
        val = getattr(payload, field)
        if val is not None:
            out[env_key] = val
    return out
