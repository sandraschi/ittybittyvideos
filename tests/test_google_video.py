import pytest

from videogen_mcp.services.google_video import (
    aspect_from_google_url,
    google_clip_url,
    google_credentials_configured,
    prompt_from_google_url,
)


def test_veo_and_omni_registered():
    from videogen_mcp.providers import list_providers

    providers = list_providers()
    assert "veo" in providers["stock"]
    assert "omni" in providers["stock"]


def test_google_clip_url_parse():
    url = google_clip_url("veo", "sunset over Vienna", "9:16")
    assert prompt_from_google_url(url) == "sunset over Vienna"
    assert aspect_from_google_url(url) == "9:16"

    omni_url = google_clip_url("omni", "cat playing", "16:9")
    assert prompt_from_google_url(omni_url) == "cat playing"
    assert aspect_from_google_url(omni_url) == "16:9"


@pytest.mark.asyncio
async def test_stock_status_veo_without_config(monkeypatch):
    monkeypatch.setenv("VIDEOGEN_STOCK_PROVIDER", "veo")
    monkeypatch.delenv("GOOGLE_AI_MCP_URL", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_CLOUD_PROJECT", raising=False)
    from videogen_mcp.config.settings import get_settings

    get_settings.cache_clear()
    from videogen_mcp.services.stock_status import stock_footage_status

    status = await stock_footage_status()
    assert status["active_provider"] == "veo"
    assert status["veo_ready"] is False
    assert status["ready_for_renders"] is False


@pytest.mark.asyncio
async def test_google_bridge_ready(monkeypatch, httpx_mock):
    monkeypatch.setenv("GOOGLE_AI_MCP_URL", "http://127.0.0.1:11014")
    from videogen_mcp.config.settings import get_settings

    get_settings.cache_clear()
    httpx_mock.add_response(url="http://127.0.0.1:11014/api/health", json={"status": "ok"})

    from videogen_mcp.services.google_video import google_backend_status

    status = await google_backend_status("veo")
    assert status["ready"] is True
    assert status["bridge_ok"] is True


def test_google_credentials_configured(monkeypatch):
    monkeypatch.setenv("GOOGLE_API_KEY", "test-key")
    from videogen_mcp.config.settings import get_settings

    get_settings.cache_clear()
    assert google_credentials_configured() is True
