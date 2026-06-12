"""Jellyfin personal-library search + stream URLs for ittybitty B-roll."""

from __future__ import annotations

from typing import Any

import httpx

from videogen_mcp.config import get_settings
from videogen_mcp.services.library_clips import LibraryClipSpec, library_clip_url, pick_clip_start

VIDEO_TYPES = "Movie,Episode,Video"
TICKS_PER_SEC = 10_000_000


def _configured() -> tuple[str, str]:
    settings = get_settings()
    base = (settings.jellyfin_server_url or settings.jellyfin_url).strip().rstrip("/")
    key = settings.jellyfin_api_key.strip()
    return base, key


def jellyfin_configured() -> bool:
    base, key = _configured()
    return bool(base and key)


async def probe_jellyfin() -> tuple[bool, str]:
    base, key = _configured()
    if not base or not key:
        return False, "Set JELLYFIN_SERVER_URL and JELLYFIN_API_KEY (same as jellyfin-mcp)"
    try:
        async with httpx.AsyncClient(timeout=8) as client:
            resp = await client.get(
                f"{base}/System/Info",
                headers={"X-Emby-Token": key},
            )
            if resp.status_code == 401:
                return False, "Jellyfin API key rejected"
            resp.raise_for_status()
            ver = resp.json().get("Version", "?")
            return True, f"Jellyfin {ver} at {base}"
    except Exception as e:
        return False, str(e)


async def _default_user_id(client: httpx.AsyncClient, base: str, key: str) -> str:
    resp = await client.get(f"{base}/Users", headers={"X-Emby-Token": key})
    resp.raise_for_status()
    users = resp.json()
    if not users:
        raise RuntimeError("No Jellyfin users found")
    return users[0]["Id"]


def _runtime_sec(item: dict[str, Any]) -> float:
    ticks = item.get("RunTimeTicks") or 0
    if ticks:
        return float(ticks) / TICKS_PER_SEC
    return float(item.get("Duration") or 0)


def _dimensions(item: dict[str, Any]) -> tuple[int, int]:
    w = int(item.get("Width") or 0)
    h = int(item.get("Height") or 0)
    if w and h:
        return w, h
    for stream in item.get("MediaStreams") or []:
        if stream.get("Type") == "Video":
            return int(stream.get("Width") or 1920), int(stream.get("Height") or 1080)
    return 1920, 1080


async def search_jellyfin_clips(
    query: str,
    count: int,
    clip_duration: float,
    aspect: str,
) -> list[LibraryClipSpec]:
    base, key = _configured()
    if not base or not key:
        return []

    async with httpx.AsyncClient(timeout=30) as client:
        user_id = await _default_user_id(client, base, key)
        resp = await client.get(
            f"{base}/Users/{user_id}/Items",
            headers={"X-Emby-Token": key},
            params={
                "SearchTerm": query,
                "IncludeItemTypes": VIDEO_TYPES,
                "Recursive": "true",
                "Limit": max(count * 3, 12),
                "Fields": "Path,MediaSources,RunTimeTicks,Width,Height,MediaStreams",
            },
        )
        resp.raise_for_status()
        items = resp.json().get("Items") or []

    specs: list[LibraryClipSpec] = []
    for item in items:
        item_id = item.get("Id")
        if not item_id:
            continue
        runtime = _runtime_sec(item)
        if runtime < clip_duration + 0.5:
            continue
        w, h = _dimensions(item)
        if aspect == "9:16" and w > h:
            continue
        if aspect == "16:9" and h > w:
            continue
        start = pick_clip_start(runtime, clip_duration, query, item_id)
        specs.append(
            LibraryClipSpec(
                backend="jellyfin",
                item_id=item_id,
                start_sec=start,
                duration_sec=clip_duration,
                query=query,
                title=str(item.get("Name") or ""),
                width=w,
                height=h,
            )
        )
        if len(specs) >= count:
            break
    return specs


async def resolve_jellyfin_source(item_id: str) -> str:
    """Direct file path when readable, else authenticated static stream URL."""
    from pathlib import Path

    base, key = _configured()
    async with httpx.AsyncClient(timeout=30) as client:
        user_id = await _default_user_id(client, base, key)
        resp = await client.get(
            f"{base}/Users/{user_id}/Items/{item_id}",
            headers={"X-Emby-Token": key},
            params={"Fields": "Path,MediaSources"},
        )
        resp.raise_for_status()
        item = resp.json()

    path = item.get("Path") or ""
    if path and Path(path).is_file():
        return path

    return f"{base}/Videos/{item_id}/stream?Static=true&api_key={key}"


def jellyfin_specs_to_stock_clips(specs: list[LibraryClipSpec]):
    from videogen_mcp.providers.base import StockClip

    return [
        StockClip(
            url=library_clip_url(s),
            duration=s.duration_sec,
            width=s.width,
            height=s.height,
            source=f"jellyfin:{s.item_id}@{s.start_sec:.1f}s",
        )
        for s in specs
    ]
