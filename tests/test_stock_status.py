import pytest

from videogen_mcp.services.stock_status import stock_footage_status


@pytest.mark.asyncio
async def test_stock_status_pexels_default(monkeypatch):
    monkeypatch.setenv("VIDEOGEN_STOCK_PROVIDER", "pexels")
    monkeypatch.setenv("PEXELS_API_KEY", "test-key")
    from videogen_mcp.config.settings import get_settings

    get_settings.cache_clear()
    status = await stock_footage_status()
    assert status["active_provider"] == "pexels"
    assert status["pexels_ready"] is True
    assert status["ready_for_renders"] is True


@pytest.mark.asyncio
async def test_stock_status_localgen_without_server(monkeypatch):
    monkeypatch.setenv("VIDEOGEN_STOCK_PROVIDER", "localgen")
    monkeypatch.setenv("COGVIDEO_URL", "http://127.0.0.1:59999")
    from videogen_mcp.config.settings import get_settings

    get_settings.cache_clear()
    status = await stock_footage_status()
    assert status["active_provider"] == "localgen"
    assert status["cogvideo_ready"] is False
    assert status["ready_for_renders"] is False
    assert "hybrid" in status["hint"].lower() or "local" in status["hint"].lower()
