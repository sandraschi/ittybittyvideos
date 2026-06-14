from __future__ import annotations

from pathlib import Path

import httpx
from loguru import logger

from videogen_mcp.config import get_settings
from videogen_mcp.providers import register_stock
from videogen_mcp.providers.base import StockClip, StockProvider

PIXABAY_VIDEOS_API = "https://pixabay.com/api/videos/"


@register_stock("pixabay")
class PixabayStockProvider(StockProvider):
    async def search(self, query: str, count: int = 5, aspect: str = "9:16") -> list[StockClip]:
        settings = get_settings()
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                PIXABAY_VIDEOS_API,
                params={
                    "key": settings.pixabay_api_key,
                    "q": query,
                    "per_page": min(max(count, 3), 200),
                    "video_type": "all",
                },
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()

        clips: list[StockClip] = []
        for hit in data.get("hits", []):
            best = _pick_video_file(hit.get("videos", {}), aspect)
            if not best:
                continue
            clips.append(
                StockClip(
                    url=best["url"],
                    duration=hit.get("duration", 10),
                    width=best.get("width", 1080),
                    height=best.get("height", 1920),
                    source=f"pixabay:{hit.get('id', '')}",
                )
            )
            if len(clips) >= count:
                break
        return clips

    async def download(self, clip: StockClip, dest: Path) -> Path:
        dest.parent.mkdir(parents=True, exist_ok=True)
        async with httpx.AsyncClient(follow_redirects=True) as client:
            resp = await client.get(clip.url, timeout=60)
            resp.raise_for_status()
            dest.write_bytes(resp.content)
        logger.debug(f"Downloaded {clip.source} -> {dest}")
        return dest

    async def health_check(self) -> bool:
        settings = get_settings()
        if not settings.pixabay_api_key:
            return False
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    PIXABAY_VIDEOS_API,
                    params={"key": settings.pixabay_api_key, "q": "nature", "per_page": 1},
                    timeout=10,
                )
                return resp.status_code == 200
        except Exception as e:
            logger.warning(f"Pixabay health check failed: {e}")
            return False


def _pick_video_file(videos: dict, aspect: str) -> dict | None:
    order = ("large", "medium", "small", "tiny")
    candidates = [videos[k] for k in order if isinstance(videos.get(k), dict) and videos[k].get("url")]
    if not candidates:
        return None
    want_portrait = aspect == "9:16"
    want_landscape = aspect == "16:9"
    if want_portrait or want_landscape:
        oriented = [
            v
            for v in candidates
            if (v.get("height", 0) > v.get("width", 0)) == want_portrait
        ]
        if oriented:
            candidates = oriented
    hd = [v for v in candidates if (v.get("height") or 0) >= 720]
    pool = hd or candidates
    pool.sort(key=lambda v: v.get("height", 0))
    return pool[0]
