from videogen_mcp.services.cache import cache_path, is_cached


def test_cache_path_deterministic():
    p1 = cache_path("https://example.com/video.mp4")
    p2 = cache_path("https://example.com/video.mp4")
    assert p1 == p2


def test_cache_path_different_urls():
    p1 = cache_path("https://example.com/a.mp4")
    p2 = cache_path("https://example.com/b.mp4")
    assert p1 != p2


def test_is_cached_returns_none_for_missing():
    result = is_cached("https://nonexistent-url-12345.com/video.mp4")
    assert result is None
