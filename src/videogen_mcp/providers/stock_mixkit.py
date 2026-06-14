from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import quote

import httpx
from loguru import logger

from videogen_mcp.providers import register_stock
from videogen_mcp.providers.base import StockClip, StockProvider

MIXKIT_CATEGORY = "https://mixkit.co/free-stock-video/{slug}/"
_MP4_1080 = re.compile(r"https://assets\.mixkit\.co/videos/\d+/\d+-1080\.mp4")


def _slugify(query: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", query.strip().lower()).strip("-")
    return slug or "nature"


@register_stock("mixkit")
class MixkitStockProvider(StockProvider):
    async def search(self, query: str, count: int = 5, aspect: str = "9:16") -> list[StockClip]:
        slug = _slugify(query.split()[0] if query else "nature")
        url = MIXKIT_CATEGORY.format(slug=quote(slug, safe="-"))
        async with httpx.AsyncClient(follow_redirects=True) as client:
            resp = await client.get(url, timeout=15, headers={"User-Agent": "ittybitty/0.2.0"})
            if resp.status_code == 404 and slug != "nature":
                resp = await client.get(MIXKIT_CATEGORY.format(slug="nature"), timeout=15)
            resp.raise_for_status()
            html = resp.text

        seen: set[str] = set()
        clips: list[StockClip] = []
        for match in _MP4_1080.finditer(html):
            mp4 = match.group(0)
            if mp4 in seen:
                continue
            seen.add(mp4)
            vid = mp4.split("/")[-1].split("-")[0]
            portrait = aspect == "9:16"
            clips.append(
                StockClip(
                    url=mp4,
                    duration=10.0,
                    width=1080 if not portrait else 608,
                    height=1920 if portrait else 1080,
                    source=f"mixkit:{vid}",
                )
            )
            if len(clips) >= count:
                break
        return clips

    async def download(self, clip: StockClip, dest: Path) -> Path:
        dest.parent.mkdir(parents=True, exist_ok=True)
        async with httpx.AsyncClient(follow_redirects=True) as client:
            resp = await client.get(clip.url, timeout=120)
            resp.raise_for_status()
            dest.write_bytes(resp.content)
        logger.debug(f"Downloaded {clip.source} -> {dest}")
        return dest

    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient(follow_redirects=True) as client:
                resp = await client.get(
                    MIXKIT_CATEGORY.format(slug="nature"),
                    timeout=10,
                    headers={"User-Agent": "ittybitty/0.2.0"},
                )
                return resp.status_code == 200 and "mixkit.co" in resp.text
        except Exception as e:
            logger.warning(f"Mixkit health check failed: {e}")
            return False
