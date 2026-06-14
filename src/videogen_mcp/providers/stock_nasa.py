from __future__ import annotations

from pathlib import Path

import httpx
from loguru import logger

from videogen_mcp.config import get_settings
from videogen_mcp.providers import register_stock
from videogen_mcp.providers.base import StockClip, StockProvider

NASA_SEARCH = "https://images-api.nasa.gov/search"
NASA_HEADERS = {"User-Agent": "ittybitty/0.2.0 (videogen-mcp)"}


def _pick_mp4_href(hrefs: list[str]) -> str | None:
    for suffix in ("~medium.mp4", "~mobile.mp4", "~preview.mp4", ".mp4"):
        for href in hrefs:
            if href.endswith(suffix):
                return href
    return None


def _mp4_from_collection(items: list) -> str | None:
    hrefs: list[str] = []
    for item in items:
        if isinstance(item, str) and item.startswith("http"):
            hrefs.append(item)
        elif isinstance(item, dict):
            href = item.get("href")
            if isinstance(href, str):
                hrefs.append(href)
    return _pick_mp4_href(hrefs)


@register_stock("nasa")
class NasaStockProvider(StockProvider):
    async def search(self, query: str, count: int = 5, aspect: str = "9:16") -> list[StockClip]:
        settings = get_settings()
        params = {"q": query or "earth", "media_type": "video", "page_size": min(count * 3, 30)}
        headers = dict(NASA_HEADERS)
        if settings.nasa_api_key:
            params["api_key"] = settings.nasa_api_key

        async with httpx.AsyncClient() as client:
            resp = await client.get(NASA_SEARCH, params=params, headers=headers, timeout=20)
            resp.raise_for_status()
            payload = resp.json()
            items = payload.get("collection", {}).get("items", [])

            clips: list[StockClip] = []
            for item in items:
                if len(clips) >= count:
                    break
                collection_href = item.get("href")
                if not collection_href:
                    continue
                meta = (item.get("data") or [{}])[0]
                nasa_id = str(meta.get("nasa_id", ""))
                coll = await client.get(collection_href, headers=headers, timeout=20)
                coll.raise_for_status()
                collection_items = coll.json()
                mp4 = _mp4_from_collection(collection_items if isinstance(collection_items, list) else [])
                if not mp4:
                    continue
                landscape = aspect == "16:9"
                clips.append(
                    StockClip(
                        url=mp4,
                        duration=30.0,
                        width=1920 if landscape else 1080,
                        height=1080 if landscape else 1920,
                        source=f"nasa:{nasa_id}",
                    )
                )
        return clips

    async def download(self, clip: StockClip, dest: Path) -> Path:
        dest.parent.mkdir(parents=True, exist_ok=True)
        async with httpx.AsyncClient(follow_redirects=True) as client:
            resp = await client.get(clip.url, timeout=180, headers=NASA_HEADERS)
            resp.raise_for_status()
            dest.write_bytes(resp.content)
        logger.debug(f"Downloaded {clip.source} -> {dest}")
        return dest

    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    NASA_SEARCH,
                    params={"q": "earth", "media_type": "video", "page_size": 1},
                    headers=NASA_HEADERS,
                    timeout=10,
                )
                return resp.status_code == 200
        except Exception as e:
            logger.warning(f"NASA health check failed: {e}")
            return False
