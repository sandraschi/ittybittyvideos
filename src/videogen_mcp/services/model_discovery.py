from __future__ import annotations

from loguru import logger
from openai import AsyncOpenAI

from videogen_mcp.config import get_settings
from videogen_mcp.services.config_store import LlmModelsResponse


async def discover_llm_models(provider: str) -> LlmModelsResponse:
    provider = provider.strip().lower()
    settings = get_settings()

    try:
        if provider == "openai":
            return await _openai_compatible_models(
                provider,
                settings.openai_api_key,
                settings.openai_base_url,
                settings.openai_model,
                require_key=True,
            )
        if provider == "deepseek":
            return await _openai_compatible_models(
                provider,
                settings.deepseek_api_key,
                settings.deepseek_base_url,
                settings.deepseek_model,
                require_key=True,
            )
        if provider == "lmstudio":
            return await _openai_compatible_models(
                provider,
                settings.lmstudio_api_key or "lm-studio",
                settings.lmstudio_base_url,
                settings.lmstudio_model,
                require_key=False,
            )
        if provider == "ollama":
            return await _openai_compatible_models(
                provider,
                "ollama",
                settings.ollama_base_url,
                settings.ollama_model,
                require_key=False,
            )
    except Exception as e:
        logger.warning(f"Model discovery failed for {provider}: {e}")
        return LlmModelsResponse(
            provider=provider,
            available=False,
            error=str(e),
            selected_model=_selected_model(provider, settings),
        )

    return LlmModelsResponse(
        provider=provider,
        available=False,
        error=f"Unknown provider: {provider}",
        selected_model="",
    )


async def discover_all_llm_models() -> list[LlmModelsResponse]:
    providers = ["deepseek", "openai", "lmstudio", "ollama"]
    results: list[LlmModelsResponse] = []
    for name in providers:
        results.append(await discover_llm_models(name))
    return results


def _selected_model(provider: str, settings) -> str:
    return {
        "openai": settings.openai_model,
        "deepseek": settings.deepseek_model,
        "lmstudio": settings.lmstudio_model,
        "ollama": settings.ollama_model,
    }.get(provider, "")


async def _openai_compatible_models(
    provider: str,
    api_key: str,
    base_url: str,
    selected: str,
    *,
    require_key: bool,
) -> LlmModelsResponse:
    if require_key and not (api_key or "").strip():
        return LlmModelsResponse(
            provider=provider,
            available=False,
            error="API key not configured",
            selected_model=selected,
        )

    client = AsyncOpenAI(api_key=api_key or "local", base_url=base_url, timeout=5.0)
    models_resp = await client.models.list()
    ids = sorted({m.id for m in models_resp.data if m.id})
    if not ids and provider == "lmstudio":
        return LlmModelsResponse(
            provider=provider,
            available=False,
            error="No model loaded in LM Studio",
            selected_model=selected,
        )

    return LlmModelsResponse(
        provider=provider,
        available=bool(ids),
        models=ids,
        selected_model=selected or (ids[0] if ids else ""),
    )
