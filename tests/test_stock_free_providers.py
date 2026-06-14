from videogen_mcp.providers.stock_coverr import _pick_mp4_url
from videogen_mcp.providers.stock_mixkit import _slugify
from videogen_mcp.providers.stock_nasa import _pick_mp4_href
from videogen_mcp.providers.stock_pixabay import _pick_video_file


def test_mixkit_slugify():
    assert _slugify("German Shepherd") == "german-shepherd"
    assert _slugify("") == "nature"


def test_nasa_pick_mp4():
    hrefs = [
        "https://images-assets.nasa.gov/video/x/x~orig.mov",
        "https://images-assets.nasa.gov/video/x/x~medium.mp4",
    ]
    assert _pick_mp4_href(hrefs).endswith("~medium.mp4")


def test_pixabay_pick_portrait_prefers_tall():
    videos = {
        "large": {"url": "http://x/l.mp4", "width": 1920, "height": 1080},
        "medium": {"url": "http://x/m.mp4", "width": 720, "height": 1280},
    }
    picked = _pick_video_file(videos, "9:16")
    assert picked["url"] == "http://x/m.mp4"


def test_coverr_pick_mp4_url():
    assert _pick_mp4_url({"mp4": "https://cdn.example/v.mp4"}) == "https://cdn.example/v.mp4"
    assert _pick_mp4_url({"preview": {"url": "https://cdn.example/p.mp4"}}) == "https://cdn.example/p.mp4"
