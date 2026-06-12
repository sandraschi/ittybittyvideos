from __future__ import annotations

from loguru import logger

from videogen_mcp.config import get_settings
from videogen_mcp.providers.base import LLMProvider

LLM_SETUP_HINT = (
    "Topic generation needs an LLM. Set DEEPSEEK_API_KEY or OPENAI_API_KEY in .env, "
    "run LM Studio or Ollama locally, or paste a custom script on Generate (skips LLM)."
)

_OPENAI_HINT = "Set OPENAI_API_KEY in .env and restart the backend."
_DEEPSEEK_HINT = "Set DEEPSEEK_API_KEY in .env and restart the backend."
_OLLAMA_HINT = "Start Ollama on http://localhost:11434 and pull a model (e.g. ollama pull llama3.2:3b)."
_LMSTUDIO_HINT = "Start LM Studio, load a model, and enable the local server on http://localhost:1234."


def _normalize_provider(name: str | None) -> str | None:
    if not name or not name.strip():
        return None
    return name.strip().lower()


async def ensure_llm_for_topic(provider: str | None = None) -> LLMProvider:
    """Resolve an LLM for topic scripting (explicit provider = no cross-fallback)."""
    from videogen_mcp.providers import get_llm

    settings = get_settings()
    chosen = _normalize_provider(provider) or _normalize_provider(settings.videogen_llm_provider) or "deepseek"

    if chosen == "openai":
        if not settings.openai_api_key.strip():
            raise ValueError(_OPENAI_HINT)
        return get_llm("openai")

    if chosen == "deepseek":
        if not settings.deepseek_api_key.strip():
            raise ValueError(_DEEPSEEK_HINT)
        llm = get_llm("deepseek")
        if not await llm.health_check():
            raise ValueError("DeepSeek API unreachable. Check DEEPSEEK_API_KEY and network.")
        return llm

    if chosen == "lmstudio":
        llm = get_llm("lmstudio")
        if not await llm.health_check():
            raise ValueError(_LMSTUDIO_HINT)
        return llm

    if chosen == "ollama":
        llm = get_llm("ollama")
        if not await llm.health_check():
            raise ValueError(_OLLAMA_HINT)
        return llm

    llm = get_llm(chosen)
    if not await llm.health_check():
        raise ValueError(f"LLM provider '{chosen}' is not ready. {LLM_SETUP_HINT}")
    return llm


async def resolve_llm_for_topic(provider: str | None = None) -> LLMProvider:
    """Auto-fallback when provider unset: cloud defaults, then LM Studio, then Ollama."""
    explicit = _normalize_provider(provider)
    if explicit:
        return await ensure_llm_for_topic(explicit)

    settings = get_settings()
    default = _normalize_provider(settings.videogen_llm_provider) or "deepseek"

    if default == "deepseek" and settings.deepseek_api_key.strip():
        try:
            return await ensure_llm_for_topic("deepseek")
        except ValueError:
            logger.warning("DeepSeek not ready; trying other LLM providers")

    if default == "openai" and settings.openai_api_key.strip():
        return await ensure_llm_for_topic("openai")

    if default == "lmstudio":
        try:
            return await ensure_llm_for_topic("lmstudio")
        except ValueError:
            logger.warning("LM Studio not ready; trying other LLM providers")

    if default == "ollama":
        return await ensure_llm_for_topic("ollama")

    if settings.deepseek_api_key.strip():
        try:
            return await ensure_llm_for_topic("deepseek")
        except ValueError:
            pass

    if settings.openai_api_key.strip():
        return await ensure_llm_for_topic("openai")

    try:
        logger.info("No cloud LLM key; trying LM Studio")
        return await ensure_llm_for_topic("lmstudio")
    except ValueError:
        pass

    logger.info("LM Studio unavailable; falling back to Ollama")
    return await ensure_llm_for_topic("ollama")


async def llm_topic_status() -> dict[str, object]:
    """Status blob for /api/v1/status and the webapp."""
    from videogen_mcp.providers import get_llm
    from videogen_mcp.providers.llm_lmstudio import LMStudioLLMProvider

    settings = get_settings()
    configured = settings.videogen_llm_provider
    openai_key_set = bool(settings.openai_api_key.strip())
    deepseek_key_set = bool(settings.deepseek_api_key.strip())
    ollama_ok = await get_llm("ollama").health_check()
    lmstudio_ok = await get_llm("lmstudio").health_check()
    lmstudio_model: str | None = None
    if lmstudio_ok:
        lmstudio_model = await LMStudioLLMProvider().loaded_model()
    deepseek_ok = False
    if deepseek_key_set:
        deepseek_ok = await get_llm("deepseek").health_check()

    ready = openai_key_set or deepseek_ok or lmstudio_ok or ollama_ok

    return {
        "configured_provider": configured,
        "openai_key_set": openai_key_set,
        "openai_ready": openai_key_set,
        "deepseek_key_set": deepseek_key_set,
        "deepseek_ready": deepseek_ok,
        "deepseek_model": settings.deepseek_model,
        "lmstudio_ready": lmstudio_ok,
        "lmstudio_model": lmstudio_model or settings.lmstudio_model or None,
        "lmstudio_base_url": settings.lmstudio_base_url,
        "ollama_reachable": ollama_ok,
        "ollama_ready": ollama_ok,
        "ollama_model": settings.ollama_model,
        "ready_for_topics": ready,
        "hint": "" if ready else LLM_SETUP_HINT,
    }
