from __future__ import annotations

import hashlib
from pathlib import Path

from videogen_mcp.config import get_settings


def cache_path(url: str, ext: str = ".mp4") -> Path:
    h = hashlib.sha256(url.encode()).hexdigest()[:16]
    p = get_settings().videogen_cache_dir / f"{h}{ext}"
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def is_cached(url: str, ext: str = ".mp4") -> Path | None:
    p = cache_path(url, ext)
    return p if p.exists() and p.stat().st_size > 0 else None
