import pytest

from videogen_mcp.providers.llm_resolve import (
    LLM_SETUP_HINT,
    ensure_llm_for_topic,
    resolve_llm_for_topic,
)


@pytest.mark.asyncio
async def test_ensure_openai_requires_key(monkeypatch):
    from videogen_mcp.config.settings import get_settings

    get_settings.cache_clear()
    monkeypatch.setenv("OPENAI_API_KEY", "")

    with pytest.raises(ValueError, match="OPENAI_API_KEY"):
        await ensure_llm_for_topic("openai")

    get_settings.cache_clear()


@pytest.mark.asyncio
async def test_ensure_ollama_requires_running(monkeypatch):
    from videogen_mcp.config.settings import get_settings

    get_settings.cache_clear()

    async def fake_health(self):
        return False

    from videogen_mcp.providers import llm_ollama

    monkeypatch.setattr(llm_ollama.OllamaLLMProvider, "health_check", fake_health)

    with pytest.raises(ValueError, match="Ollama"):
        await ensure_llm_for_topic("ollama")

    get_settings.cache_clear()


@pytest.mark.asyncio
async def test_ensure_deepseek_requires_key(monkeypatch):
    from videogen_mcp.config.settings import get_settings

    get_settings.cache_clear()
    monkeypatch.setenv("DEEPSEEK_API_KEY", "")

    with pytest.raises(ValueError, match="DEEPSEEK_API_KEY"):
        await ensure_llm_for_topic("deepseek")

    get_settings.cache_clear()


@pytest.mark.asyncio
async def test_resolve_prefers_deepseek_when_configured(monkeypatch):
    from videogen_mcp.config.settings import get_settings

    get_settings.cache_clear()
    monkeypatch.setenv("VIDEOGEN_LLM_PROVIDER", "deepseek")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test")

    async def fake_health(self):
        return True

    from videogen_mcp.providers import llm_deepseek

    monkeypatch.setattr(llm_deepseek.DeepSeekLLMProvider, "health_check", fake_health)

    llm = await resolve_llm_for_topic(None)
    assert llm.__class__.__name__ == "DeepSeekLLMProvider"

    get_settings.cache_clear()


@pytest.mark.asyncio
async def test_ensure_lmstudio_requires_server(monkeypatch):
    from videogen_mcp.config.settings import get_settings

    get_settings.cache_clear()

    async def fake_health(self):
        return False

    from videogen_mcp.providers import llm_lmstudio

    monkeypatch.setattr(llm_lmstudio.LMStudioLLMProvider, "health_check", fake_health)

    with pytest.raises(ValueError, match="LM Studio"):
        await ensure_llm_for_topic("lmstudio")

    get_settings.cache_clear()


@pytest.mark.asyncio
async def test_resolve_falls_back_to_ollama(monkeypatch):
    from videogen_mcp.config.settings import get_settings

    get_settings.cache_clear()
    monkeypatch.setenv("VIDEOGEN_LLM_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "")

    async def fake_health(self):
        return True

    async def fake_lmstudio_health(self):
        return False

    from videogen_mcp.providers import llm_lmstudio, llm_ollama

    monkeypatch.setattr(llm_lmstudio.LMStudioLLMProvider, "health_check", fake_lmstudio_health)
    monkeypatch.setattr(llm_ollama.OllamaLLMProvider, "health_check", fake_health)

    llm = await resolve_llm_for_topic(None)
    assert llm.__class__.__name__ == "OllamaLLMProvider"

    get_settings.cache_clear()


@pytest.mark.asyncio
async def test_resolve_openai_when_key_set(monkeypatch):
    from videogen_mcp.config.settings import get_settings

    get_settings.cache_clear()
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")

    llm = await resolve_llm_for_topic(None)
    assert llm.__class__.__name__ == "OpenAILLMProvider"

    get_settings.cache_clear()


def test_llm_setup_hint_is_actionable():
    assert "OPENAI_API_KEY" in LLM_SETUP_HINT
    assert "custom script" in LLM_SETUP_HINT
