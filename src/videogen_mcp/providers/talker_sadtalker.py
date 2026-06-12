"""SadTalker-contract talking-head provider (SPEC R9).

Talks to any external FOSS talking-head service exposing the minimal
contract below -- SadTalker, EchoMimic, Hallo2, or LivePortrait (animals
mode works for pets) behind a thin wrapper:

    POST {TALKER_URL}/generate   multipart: audio=<wav/mp3>, image=<png/jpg>
    -> 200 with video/mp4 bytes, or JSON error

The model service is external by design (LLM_AND_INSTALL_TIERS: never
bundle models). When the backend is unreachable, errors are explicit --
the pipeline logs and ships the video without the overlay.
"""

from __future__ import annotations

from pathlib import Path

import httpx
from loguru import logger

from videogen_mcp.config import get_settings
from videogen_mcp.providers import register_talker
from videogen_mcp.providers.base import TalkerProvider

_TIMEOUT = httpx.Timeout(connect=10.0, read=600.0, write=120.0, pool=10.0)


@register_talker("sadtalker")
class SadTalkerProvider(TalkerProvider):
    def __init__(self) -> None:
        self.base_url = get_settings().talker_url.rstrip("/")

    async def synthesize_head(self, audio_path: Path, source_image: Path, output_path: Path) -> Path:
        if not source_image.exists():
            raise FileNotFoundError(f"Talker source image not found: {source_image}")
        if not audio_path.exists():
            raise FileNotFoundError(f"Narration audio not found: {audio_path}")

        logger.info(f"Talker: {source_image.name} + {audio_path.name} -> {self.base_url}/generate")
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            with open(audio_path, "rb") as af, open(source_image, "rb") as imf:
                resp = await client.post(
                    f"{self.base_url}/generate",
                    files={
                        "audio": (audio_path.name, af, "application/octet-stream"),
                        "image": (source_image.name, imf, "application/octet-stream"),
                    },
                )
        if resp.status_code != 200:
            raise RuntimeError(f"Talker backend {self.base_url} returned {resp.status_code}: {resp.text[:200]}")
        content_type = resp.headers.get("content-type", "")
        if "video" not in content_type and not resp.content[:8].startswith(b"\x00\x00\x00"):
            raise RuntimeError(f"Talker backend returned non-video content ({content_type})")

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(resp.content)
        logger.info(f"Talker: head video {output_path.name} ({len(resp.content) / 1024 / 1024:.1f} MB)")
        return output_path

    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{self.base_url}/health")
                return resp.status_code == 200
        except Exception as e:
            logger.warning(f"Talker health check failed ({self.base_url}): {e}")
            return False
