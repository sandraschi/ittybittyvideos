"""Google cloud generated footage — Veo 3.x and Gemini Omni Flash."""

from __future__ import annotations

from pathlib import Path

from loguru import logger

from videogen_mcp.config import get_settings
from videogen_mcp.providers import register_stock
from videogen_mcp.providers.base import StockClip, StockProvider
from videogen_mcp.services.google_video import (
    GoogleBackend,
    aspect_from_google_url,
    generate_google_clip,
    google_backend_status,
    google_clip_url,
    prompt_from_google_url,
)


class _GoogleVideoStockProvider(StockProvider):
    backend: GoogleBackend = "veo"

    async def search(self, query: str, count: int = 1, aspect: str = "9:16") -> list[StockClip]:
        dims = {
            "9:16": (720, 1280),
            "16:9": (1280, 720),
            "1:1": (720, 720),
        }
        width, height = dims.get(aspect, (720, 1280))
        clip_duration = 8.0 if self.backend == "veo" else 10.0
        return [
            StockClip(
                url=google_clip_url(self.backend, query, aspect),
                duration=clip_duration,
                width=width,
                height=height,
                source=f"{self.backend}:{query[:30]}",
            )
            for _ in range(min(count, 2))
        ]

    async def download(self, clip: StockClip, dest: Path) -> Path:
        prompt = prompt_from_google_url(clip.url)
        aspect = aspect_from_google_url(clip.url)
        settings = get_settings()
        duration = settings.videogen_clip_duration
        out = await generate_google_clip(self.backend, prompt, aspect, dest, duration)
        logger.debug(f"Google {self.backend} clip: {prompt[:50]} -> {out}")
        return out

    async def health_check(self) -> bool:
        status = await google_backend_status(self.backend)
        return bool(status["ready"])


@register_stock("veo")
class VeoStockProvider(_GoogleVideoStockProvider):
    backend = "veo"


@register_stock("omni")
class OmniStockProvider(_GoogleVideoStockProvider):
    backend = "omni"
