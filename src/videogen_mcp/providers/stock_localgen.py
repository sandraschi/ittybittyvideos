"""Local AI video generation — Wan 2.2 sidecar (2026 tier).

Calls the roughcutvideos LocalGen HTTP server (default :8188). Legacy env COGVIDEO_URL
still works. Set VIDEOGEN_STOCK_PROVIDER=localgen (or cogvideo alias).
"""

from __future__ import annotations

from pathlib import Path
from urllib.parse import parse_qs, quote, unquote, urlparse

import httpx
from loguru import logger

from videogen_mcp.config import get_settings
from videogen_mcp.providers import register_stock
from videogen_mcp.providers.base import StockClip, StockProvider


def _prompt_from_clip_url(url: str) -> str:
    if "prompt=" in url:
        parsed = urlparse(url)
        if parsed.scheme in ("localgen", "cogvideo"):
            qs = parse_qs(parsed.query)
            if qs.get("prompt"):
                return unquote(qs["prompt"][0])
        return unquote(url.split("prompt=", 1)[1].split("&", 1)[0])
    return "cinematic scene"


def _aspect_from_clip_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme in ("localgen", "cogvideo"):
        qs = parse_qs(parsed.query)
        if qs.get("aspect"):
            return qs["aspect"][0]
    if "aspect=" in url:
        return url.split("aspect=", 1)[1].split("&", 1)[0]
    return "9:16"


@register_stock("localgen")
class LocalGenStockProvider(StockProvider):
    def _base_url(self) -> str:
        settings = get_settings()
        return (settings.localgen_url or settings.cogvideo_url).rstrip("/")

    async def search(self, query: str, count: int = 1, aspect: str = "9:16") -> list[StockClip]:
        prompt = quote(query, safe="")
        return [
            StockClip(
                url=f"localgen://generate?prompt={prompt}&aspect={aspect}",
                duration=5.0,
                width={"9:16": 720, "16:9": 1280, "1:1": 720}.get(aspect, 720),
                height={"9:16": 1280, "16:9": 720, "1:1": 720}.get(aspect, 1280),
                source=f"localgen:{query[:30]}",
            )
            for _ in range(min(count, 2))
        ]

    async def download(self, clip: StockClip, dest: Path) -> Path:
        base = self._base_url()
        prompt = _prompt_from_clip_url(clip.url)
        aspect = _aspect_from_clip_url(clip.url)

        dest.parent.mkdir(parents=True, exist_ok=True)
        async with httpx.AsyncClient(timeout=600) as client:
            resp = await client.post(
                f"{base}/api/generate",
                json={
                    "prompt": prompt,
                    "aspect": aspect,
                    "num_frames": 81,
                    "guidance_scale": 5.0,
                },
            )
            resp.raise_for_status()
            dest.write_bytes(resp.content)

        logger.debug(f"LocalGen clip: {prompt[:50]} -> {dest}")
        return dest

    async def health_check(self) -> bool:
        base = self._base_url()
        if not base:
            return False
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get(f"{base}/api/health")
                if resp.status_code != 200:
                    return False
                body = resp.json()
                return body.get("status") == "ok" and body.get("deps_installed", True)
        except Exception as e:
            logger.warning(f"LocalGen health check failed: {e}")
            return False
