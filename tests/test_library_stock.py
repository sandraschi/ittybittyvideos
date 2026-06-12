import pytest

from videogen_mcp.providers import list_providers
from videogen_mcp.services.library_clips import (
    LibraryClipSpec,
    library_clip_url,
    parse_library_clip_url,
    pick_clip_start,
)


def test_jellyfin_and_plex_registered():
    providers = list_providers()
    assert "jellyfin" in providers["stock"]
    assert "plex" in providers["stock"]


def test_library_clip_url_roundtrip():
    spec = LibraryClipSpec(
        backend="jellyfin",
        item_id="abc-123",
        start_sec=12.5,
        duration_sec=5.0,
        query="dog beach",
        title="Vacation 2024",
        width=1920,
        height=1080,
    )
    url = library_clip_url(spec)
    parsed = parse_library_clip_url(url)
    assert parsed.backend == "jellyfin"
    assert parsed.item_id == "abc-123"
    assert parsed.start_sec == 12.5
    assert parsed.duration_sec == 5.0
    assert parsed.query == "dog beach"
    assert parsed.title == "Vacation 2024"


def test_pick_clip_start_bounded():
    start = pick_clip_start(120.0, 5.0, "dog", "item1")
    assert 0 <= start <= 115.0
    assert pick_clip_start(4.0, 5.0, "x", "y") == 0.0


@pytest.mark.asyncio
async def test_jellyfin_stock_search_mock(monkeypatch):
    monkeypatch.setenv("JELLYFIN_SERVER_URL", "http://127.0.0.1:8096")
    monkeypatch.setenv("JELLYFIN_API_KEY", "test-key")
    from videogen_mcp.config.settings import get_settings

    get_settings.cache_clear()

    async def fake_search(query, count, clip_duration, aspect):
        return [
            LibraryClipSpec(
                backend="jellyfin",
                item_id="vid1",
                start_sec=10.0,
                duration_sec=5.0,
                query=query,
                title="Dog park",
                width=1920,
                height=1080,
            )
        ]

    monkeypatch.setattr("videogen_mcp.providers.stock_library.search_jellyfin_clips", fake_search)

    from videogen_mcp.providers.stock_library import JellyfinStockProvider

    provider = JellyfinStockProvider()
    clips = await provider.search("dog", count=1, aspect="16:9")
    assert len(clips) == 1
    assert clips[0].source.startswith("jellyfin:vid1")


@pytest.mark.asyncio
async def test_stock_status_jellyfin_not_configured(monkeypatch):
    monkeypatch.setenv("VIDEOGEN_STOCK_PROVIDER", "jellyfin")
    monkeypatch.delenv("JELLYFIN_SERVER_URL", raising=False)
    monkeypatch.delenv("JELLYFIN_API_KEY", raising=False)
    from videogen_mcp.config.settings import get_settings

    get_settings.cache_clear()
    from videogen_mcp.services.stock_status import stock_footage_status

    status = await stock_footage_status()
    assert status["active_provider"] == "jellyfin"
    assert status["ready_for_renders"] is False
    assert status["jellyfin_ready"] is False
