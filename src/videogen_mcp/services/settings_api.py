from __future__ import annotations

from videogen_mcp.config import get_settings
from videogen_mcp.providers.llm_resolve import llm_topic_status
from videogen_mcp.services.config_store import (
    SECRET_MASK,
    ProviderSettingsPublic,
    SettingsPublic,
    SettingsUpdate,
    _hint_secret,
    env_file_path,
    reload_settings,
    settings_update_to_env,
    write_env_map,
)
from videogen_mcp.services.model_discovery import discover_all_llm_models
from videogen_mcp.services.stock_status import stock_footage_status


async def get_public_settings() -> SettingsPublic:
    settings = get_settings()
    llm_status = await llm_topic_status()
    stock = await stock_footage_status()

    providers = [
        ProviderSettingsPublic(
            id="deepseek",
            label="DeepSeek V4 Flash",
            ready=bool(llm_status.get("deepseek_ready")),
            model=settings.deepseek_model,
            base_url=settings.deepseek_base_url,
            api_key_set=bool(settings.deepseek_api_key.strip()),
            api_key_hint=_hint_secret(settings.deepseek_api_key),
        ),
        ProviderSettingsPublic(
            id="openai",
            label="OpenAI",
            ready=bool(llm_status.get("openai_ready")),
            model=settings.openai_model,
            base_url=settings.openai_base_url,
            api_key_set=bool(settings.openai_api_key.strip()),
            api_key_hint=_hint_secret(settings.openai_api_key),
        ),
        ProviderSettingsPublic(
            id="lmstudio",
            label="LM Studio",
            ready=bool(llm_status.get("lmstudio_ready")),
            model=settings.lmstudio_model or str(llm_status.get("lmstudio_model") or ""),
            base_url=settings.lmstudio_base_url,
            api_key_set=True,
            api_key_hint="local",
        ),
        ProviderSettingsPublic(
            id="ollama",
            label="Ollama",
            ready=bool(llm_status.get("ollama_ready")),
            model=settings.ollama_model,
            base_url=settings.ollama_base_url,
            api_key_set=True,
            api_key_hint="local",
        ),
    ]

    return SettingsPublic(
        env_path=str(env_file_path()),
        videogen_llm_provider=settings.videogen_llm_provider,
        llm_providers=providers,
        videogen_stock_provider=settings.videogen_stock_provider,
        pexels_api_key_set=bool(settings.pexels_api_key.strip()),
        pexels_api_key_hint=_hint_secret(settings.pexels_api_key),
        cogvideo_url=settings.cogvideo_url,
        cogvideo_ready=bool(stock["cogvideo_ready"]),
        cogvideo_error=str(stock["cogvideo_error"]),
        google_api_key_set=bool(settings.google_api_key.strip()),
        google_api_key_hint=_hint_secret(settings.google_api_key),
        google_cloud_project=settings.google_cloud_project,
        google_ai_mcp_url=settings.google_ai_mcp_url,
        veo_ready=bool(stock["veo_ready"]),
        omni_ready=bool(stock["omni_ready"]),
        stock_ready_for_renders=bool(stock["ready_for_renders"]),
        stock_hint=str(stock["hint"]),
        videogen_tts_provider=settings.videogen_tts_provider,
        edge_tts_voice=settings.edge_tts_voice,
    )


async def save_settings(payload: SettingsUpdate) -> SettingsPublic:
    write_env_map(settings_update_to_env(payload))
    reload_settings()
    return await get_public_settings()


async def get_settings_with_models() -> dict:
    settings = await get_public_settings()
    models = await discover_all_llm_models()
    return {
        "success": True,
        "settings": settings.model_dump(),
        "models": [m.model_dump() for m in models],
        "secret_mask": SECRET_MASK,
    }
