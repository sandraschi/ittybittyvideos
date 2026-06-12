from __future__ import annotations

from pathlib import Path

import httpx
from loguru import logger

from videogen_mcp.config import get_settings
from videogen_mcp.providers import register_stock
from videogen_mcp.providers.base import StockClip, StockProvider

PEXELS_API = "https://api.pexels.com/videos/search"


@register_stock("pexels")
class PexelsStockProvider(StockProvider):
    async def search(self, query: str, count: int = 5, aspect: str = "9:16") -> list[StockClip]:
        settings = get_settings()
        orientation = {"9:16": "portrait", "16:9": "landscape", "1:1": "square"}.get(aspect, "portrait")
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                PEXELS_API,
                params={"query": query, "per_page": count, "orientation": orientation},
                headers={"Authorization": settings.pexels_api_key},
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()

        clips = []
        for video in data.get("videos", []):
            best = _pick_best_file(video.get("video_files", []))
            if best:
                clips.append(
                    StockClip(
                        url=best["link"],
                        duration=video.get("duration", 10),
                        width=best.get("width", 1080),
                        height=best.get("height", 1920),
                        source=f"pexels:{video.get('id', '')}",
                    )
                )
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
        if not settings.pexels_api_key:
            return False
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    PEXELS_API,
                    params={"query": "nature", "per_page": 1},
                    headers={"Authorization": settings.pexels_api_key},
                    timeout=10,
                )
                return resp.status_code == 200
        except Exception as e:
            logger.warning(f"Pexels health check failed: {e}")
            return False


def _pick_best_file(files: list[dict]) -> dict | None:
    mp4s = [f for f in files if f.get("file_type") == "video/mp4"]
    if not mp4s:
        mp4s = files
    hd = [f for f in mp4s if (f.get("height") or 0) >= 720]
    if hd:
        hd.sort(key=lambda f: f.get("height", 0))
        return hd[0]
    return mp4s[0] if mp4s else None
