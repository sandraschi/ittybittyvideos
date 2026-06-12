"""CogVideoX AI video generation provider -- Tsinghua/ZhipuAI open-weight video model.

CogVideoX generates 6-second video clips from text prompts. Replaces stock
footage with AI-generated footage for scenes where stock search terms don't
match well (abstract concepts, specific actions, branded content).

Expects CogVideoX server at COGVIDEO_URL (default http://localhost:8188)
running via ComfyUI or the official inference server, OR ZhipuAI cloud API.
"""

from __future__ import annotations

import os
from pathlib import Path

import httpx
from loguru import logger

from videogen_mcp.providers import register_stock
from videogen_mcp.providers.base import StockClip, StockProvider


@register_stock("cogvideo")
class CogVideoStockProvider(StockProvider):
    async def search(self, query: str, count: int = 1, aspect: str = "9:16") -> list[StockClip]:
        return [
            StockClip(
                url=f"cogvideo://generate?prompt={query}&aspect={aspect}",
                duration=6.0,
                width={"9:16": 720, "16:9": 1280, "1:1": 720}.get(aspect, 720),
                height={"9:16": 1280, "16:9": 720, "1:1": 720}.get(aspect, 1280),
                source=f"cogvideo:{query[:30]}",
            )
            for _ in range(min(count, 2))
        ]

    async def download(self, clip: StockClip, dest: Path) -> Path:
        url = os.environ.get("COGVIDEO_URL", "http://localhost:8188")
        prompt = clip.url.split("prompt=")[1].split("&")[0] if "prompt=" in clip.url else "cinematic scene"

        dest.parent.mkdir(parents=True, exist_ok=True)
        async with httpx.AsyncClient(timeout=300) as client:
            resp = await client.post(
                f"{url}/api/generate",
                json={"prompt": prompt, "num_frames": 49, "guidance_scale": 6.0},
            )
            resp.raise_for_status()

            video_url = resp.json().get("video_url", "")
            if video_url:
                video_resp = await client.get(video_url, timeout=120)
                dest.write_bytes(video_resp.content)
            else:
                dest.write_bytes(resp.content)

        logger.debug(f"CogVideoX generated: {prompt[:50]} -> {dest}")
        return dest

    async def health_check(self) -> bool:
        url = os.environ.get("COGVIDEO_URL", "http://localhost:8188")
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get(f"{url}/api/health")
                return resp.status_code == 200
        except Exception as e:
            logger.warning(f"CogVideoX health check failed: {e}")
            return False
