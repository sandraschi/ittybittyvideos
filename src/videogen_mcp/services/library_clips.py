"""Shared helpers: library clip URLs and ffmpeg segment extraction."""

from __future__ import annotations

import hashlib
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import parse_qs, quote, unquote, urlparse

from loguru import logger


@dataclass(frozen=True)
class LibraryClipSpec:
    backend: str  # jellyfin | plex
    item_id: str
    start_sec: float
    duration_sec: float
    query: str
    title: str = ""
    width: int = 1920
    height: int = 1080


def pick_clip_start(duration_sec: float, clip_len: float, query: str, item_id: str) -> float:
    """Deterministic pseudo-random in-point so repeated renders vary but stay stable per item."""
    if duration_sec <= clip_len + 1:
        return 0.0
    digest = hashlib.sha256(f"{query}:{item_id}".encode()).hexdigest()
    bucket = int(digest[:8], 16)
    max_start = max(1.0, duration_sec - clip_len - 0.5)
    return (bucket % int(max_start * 10)) / 10.0


def library_clip_url(spec: LibraryClipSpec) -> str:
    q = quote(spec.query, safe="")
    title = quote(spec.title, safe="")
    return (
        f"{spec.backend}://clip?"
        f"item={quote(spec.item_id, safe='')}"
        f"&start={spec.start_sec:.2f}"
        f"&duration={spec.duration_sec:.2f}"
        f"&query={q}"
        f"&title={title}"
        f"&w={spec.width}"
        f"&h={spec.height}"
    )


def parse_library_clip_url(url: str) -> LibraryClipSpec:
    parsed = urlparse(url)
    if parsed.scheme not in ("jellyfin", "plex"):
        raise ValueError(f"Not a library clip URL: {url}")
    qs = parse_qs(parsed.query)
    item = (qs.get("item") or [""])[0]
    if not item:
        raise ValueError("library clip URL missing item id")
    start = float((qs.get("start") or ["0"])[0])
    duration = float((qs.get("duration") or ["5"])[0])
    query = unquote((qs.get("query") or [""])[0])
    title = unquote((qs.get("title") or [""])[0])
    width = int((qs.get("w") or ["1920"])[0])
    height = int((qs.get("h") or ["1080"])[0])
    return LibraryClipSpec(
        backend=parsed.scheme,
        item_id=item,
        start_sec=start,
        duration_sec=duration,
        query=query,
        title=title,
        width=width,
        height=height,
    )


def ffmpeg_extract_clip(source: str, dest: Path, start_sec: float, duration_sec: float) -> Path:
    """Cut a segment with ffmpeg (-ss before -i for HTTP streams)."""
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("FFmpeg not found on PATH — required for library clip extraction")

    dest.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        ffmpeg,
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-ss",
        f"{start_sec:.3f}",
        "-i",
        source,
        "-t",
        f"{duration_sec:.3f}",
        "-an",
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-crf",
        "23",
        "-movflags",
        "+faststart",
        str(dest),
    ]
    logger.debug(f"ffmpeg library clip: start={start_sec:.1f}s dur={duration_sec:.1f}s")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if result.returncode != 0:
        tail = (result.stderr or result.stdout or "").strip()[-500:]
        raise RuntimeError(f"ffmpeg clip extract failed: {tail}")
    if not dest.is_file() or dest.stat().st_size < 1024:
        raise RuntimeError("ffmpeg produced empty library clip")
    return dest
