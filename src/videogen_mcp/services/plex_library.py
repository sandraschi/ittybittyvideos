"""Plex personal-library search + stream URLs for roughcut B-roll."""

from __future__ import annotations

from typing import Any
from urllib.parse import urljoin

import httpx

from videogen_mcp.config import get_settings
from videogen_mcp.services.library_clips import LibraryClipSpec, library_clip_url, pick_clip_start


def _configured() -> tuple[str, str]:
    settings = get_settings()
    base = (settings.plex_url or settings.plex_server_url).strip().rstrip("/")
    token = settings.plex_token.strip()
    return base, token


def plex_configured() -> bool:
    base, token = _configured()
    return bool(base and token)


async def probe_plex() -> tuple[bool, str]:
    base, token = _configured()
    if not base or not token:
        return False, "Set PLEX_URL and PLEX_TOKEN (same as plex-mcp)"
    try:
        async with httpx.AsyncClient(timeout=8) as client:
            resp = await client.get(
                f"{base}/",
                headers={"X-Plex-Token": token, "Accept": "application/json"},
            )
            if resp.status_code == 401:
                return False, "Plex token rejected"
            resp.raise_for_status()
            name = resp.json().get("MediaContainer", {}).get("friendlyName", "Plex")
            return True, f"{name} at {base}"
    except Exception as e:
        return False, str(e)


def _video_hits(payload: dict[str, Any]) -> list[dict[str, Any]]:
    container = payload.get("MediaContainer") or {}
    hits: list[dict[str, Any]] = []
    for meta in container.get("Metadata") or []:
        hits.append(meta)
    for group in container.get("SearchResult") or []:
        for meta in group.get("Metadata") or []:
            hits.append(meta)
    return hits


def _duration_sec(meta: dict[str, Any]) -> float:
    ms = meta.get("duration") or meta.get("Duration")
    if ms is None:
        return 0.0
    return float(ms) / 1000.0


def _dimensions(meta: dict[str, Any]) -> tuple[int, int]:
    media_list = meta.get("Media") or []
    if media_list:
        w = int(media_list[0].get("width") or media_list[0].get("Width") or 0)
        h = int(media_list[0].get("height") or media_list[0].get("Height") or 0)
        if w and h:
            return w, h
    return 1920, 1080


async def search_plex_clips(
    query: str,
    count: int,
    clip_duration: float,
    aspect: str,
) -> list[LibraryClipSpec]:
    base, token = _configured()
    if not base or not token:
        return []

    headers = {"X-Plex-Token": token, "Accept": "application/json"}
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(
            f"{base}/search",
            headers=headers,
            params={"query": query, "limit": max(count * 3, 12)},
        )
        resp.raise_for_status()
        hits = _video_hits(resp.json())

    specs: list[LibraryClipSpec] = []
    for meta in hits:
        if meta.get("type") not in ("movie", "episode", "clip", "video"):
            continue
        rating_key = str(meta.get("ratingKey") or meta.get("ratingkey") or "")
        if not rating_key:
            continue
        runtime = _duration_sec(meta)
        if runtime < clip_duration + 0.5:
            continue
        w, h = _dimensions(meta)
        if aspect == "9:16" and w > h:
            continue
        if aspect == "16:9" and h > w:
            continue
        start = pick_clip_start(runtime, clip_duration, query, rating_key)
        specs.append(
            LibraryClipSpec(
                backend="plex",
                item_id=rating_key,
                start_sec=start,
                duration_sec=clip_duration,
                query=query,
                title=str(meta.get("title") or meta.get("Title") or ""),
                width=w,
                height=h,
            )
        )
        if len(specs) >= count:
            break
    return specs


async def resolve_plex_source(rating_key: str) -> str:
    base, token = _configured()
    headers = {"X-Plex-Token": token, "Accept": "application/json"}
    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        resp = await client.get(f"{base}/library/metadata/{rating_key}", headers=headers)
        resp.raise_for_status()
        meta = (resp.json().get("MediaContainer") or {}).get("Metadata") or []
        if not meta:
            raise RuntimeError(f"Plex item not found: {rating_key}")
        item = meta[0]
        media = (item.get("Media") or [{}])[0]
        part = (media.get("Part") or [{}])[0]
        part_key = part.get("key") or ""
        if not part_key:
            raise RuntimeError(f"Plex item has no media part: {rating_key}")
        sep = "&" if "?" in part_key else "?"
        return urljoin(f"{base}/", f"{part_key}{sep}X-Plex-Token={token}")


def plex_specs_to_stock_clips(specs: list[LibraryClipSpec]):
    from videogen_mcp.providers.base import StockClip

    return [
        StockClip(
            url=library_clip_url(s),
            duration=s.duration_sec,
            width=s.width,
            height=s.height,
            source=f"plex:{s.item_id}@{s.start_sec:.1f}s",
        )
        for s in specs
    ]
