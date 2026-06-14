from __future__ import annotations

from pathlib import Path

import httpx
from loguru import logger

from videogen_mcp.config import get_settings
from videogen_mcp.providers import register_stock
from videogen_mcp.providers.base import StockClip, StockProvider

COVERR_API = "https://api.coverr.co/videos"


@register_stock("coverr")
class CoverrStockProvider(StockProvider):
    async def search(self, query: str, count: int = 5, aspect: str = "9:16") -> list[StockClip]:
        settings = get_settings()
        params: dict[str, str | int | bool] = {
            "query": query,
            "page_size": min(max(count, 3), 50),
            "urls": True,
            "sort": "popular",
        }
        headers: dict[str, str] = {"Authorization": f"Bearer {settings.coverr_api_key}"}

        async with httpx.AsyncClient() as client:
            resp = await client.get(COVERR_API, params=params, headers=headers, timeout=15)
            resp.raise_for_status()
            data = resp.json()

        clips: list[StockClip] = []
        for hit in data.get("hits", []):
            if aspect == "9:16" and not hit.get("is_vertical", False):
                continue
            if aspect == "16:9" and hit.get("is_vertical", False):
                continue
            url = _pick_mp4_url(hit.get("urls") or {})
            if not url:
                continue
            clips.append(
                StockClip(
                    url=url,
                    duration=hit.get("duration") or 10,
                    width=1080 if hit.get("is_vertical") else 1920,
                    height=1920 if hit.get("is_vertical") else 1080,
                    source=f"coverr:{hit.get('id', hit.get('slug', ''))}",
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
        if not settings.coverr_api_key:
            return False
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    COVERR_API,
                    params={"page_size": 1, "urls": True},
                    headers={"Authorization": f"Bearer {settings.coverr_api_key}"},
                    timeout=10,
                )
                return resp.status_code == 200
        except Exception as e:
            logger.warning(f"Coverr health check failed: {e}")
            return False


def _pick_mp4_url(urls: dict) -> str | None:
    for key in ("mp4", "mp4_download", "mp4_preview", "preview", "hd", "sd"):
        val = urls.get(key)
        if isinstance(val, str) and val.startswith("http"):
            return val
        if isinstance(val, dict) and val.get("url"):
            return str(val["url"])
    for val in urls.values():
        if isinstance(val, str) and val.endswith(".mp4"):
            return val
    return None
