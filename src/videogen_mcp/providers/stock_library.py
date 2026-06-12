from __future__ import annotations

import asyncio
from pathlib import Path

from loguru import logger

from videogen_mcp.config import get_settings
from videogen_mcp.providers import register_stock
from videogen_mcp.providers.base import StockClip, StockProvider
from videogen_mcp.services.jellyfin_library import (
    jellyfin_specs_to_stock_clips,
    probe_jellyfin,
    resolve_jellyfin_source,
    search_jellyfin_clips,
)
from videogen_mcp.services.library_clips import ffmpeg_extract_clip, parse_library_clip_url
from videogen_mcp.services.plex_library import (
    plex_specs_to_stock_clips,
    probe_plex,
    resolve_plex_source,
    search_plex_clips,
)


def _clip_duration(settings) -> float:
    return max(2.0, float(settings.videogen_clip_duration or 5.0))


@register_stock("jellyfin")
class JellyfinStockProvider(StockProvider):
    async def search(self, query: str, count: int = 5, aspect: str = "9:16") -> list[StockClip]:
        settings = get_settings()
        specs = await search_jellyfin_clips(query, count, _clip_duration(settings), aspect)
        if not specs:
            logger.warning(f"Jellyfin: no clips for query {query!r}")
        return jellyfin_specs_to_stock_clips(specs)

    async def download(self, clip: StockClip, dest: Path) -> Path:
        spec = parse_library_clip_url(clip.url)
        source = await resolve_jellyfin_source(spec.item_id)
        return await asyncio.to_thread(
            ffmpeg_extract_clip, source, dest, spec.start_sec, spec.duration_sec
        )

    async def health_check(self) -> bool:
        ok, _ = await probe_jellyfin()
        return ok


@register_stock("plex")
class PlexStockProvider(StockProvider):
    async def search(self, query: str, count: int = 5, aspect: str = "9:16") -> list[StockClip]:
        settings = get_settings()
        specs = await search_plex_clips(query, count, _clip_duration(settings), aspect)
        if not specs:
            logger.warning(f"Plex: no clips for query {query!r}")
        return plex_specs_to_stock_clips(specs)

    async def download(self, clip: StockClip, dest: Path) -> Path:
        spec = parse_library_clip_url(clip.url)
        source = await resolve_plex_source(spec.item_id)
        return await asyncio.to_thread(
            ffmpeg_extract_clip, source, dest, spec.start_sec, spec.duration_sec
        )

    async def health_check(self) -> bool:
        ok, _ = await probe_plex()
        return ok
