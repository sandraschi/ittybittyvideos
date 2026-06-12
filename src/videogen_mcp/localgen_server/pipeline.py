from __future__ import annotations

import asyncio
import os
import tempfile
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from videogen_mcp.localgen_server.backends import BACKENDS, DEFAULT_BACKEND
from videogen_mcp.localgen_server.backends.loader import (
    backend_meta,
    generate_sync,
    load_pipeline,
    resolve_backend_key,
)

_lock = threading.Lock()
_pipeline: Any = None
_meta: dict[str, str] | None = None


@dataclass
class RuntimeInfo:
    backend: str
    model_id: str
    label: str
    tier: str
    device: str
    cuda_available: bool
    deps_installed: bool
    memory_mode: str = ""
    load_error: str = ""


def _cuda_available() -> bool:
    try:
        import torch

        return bool(torch.cuda.is_available())
    except ImportError:
        return False


def _deps_installed() -> bool:
    try:
        import torch  # noqa: F401

        key = resolve_backend_key()
        if key.startswith("cogvideo"):
            from diffusers import CogVideoXPipeline  # noqa: F401

            return True
        from diffusers import WanPipeline  # noqa: F401

        return True
    except ImportError:
        return False


def get_runtime_info() -> RuntimeInfo:
    key = resolve_backend_key()
    meta = BACKENDS.get(key, BACKENDS[DEFAULT_BACKEND])
    cuda = _cuda_available()
    return RuntimeInfo(
        backend=key,
        model_id=os.environ.get("LOCALGEN_MODEL") or meta["model_id"],
        label=meta["label"],
        tier=meta["tier"],
        device=os.environ.get("LOCALGEN_DEVICE", "cuda" if cuda else "cpu"),
        cuda_available=cuda,
        deps_installed=_deps_installed(),
        memory_mode=_meta.get("memory_mode", "") if _meta else "",
    )


def is_model_loaded() -> bool:
    return _pipeline is not None


def preload_pipeline() -> None:
    with _lock:
        _ensure_pipeline()


def _ensure_pipeline() -> Any:
    global _pipeline, _meta
    if _pipeline is not None:
        return _pipeline
    _pipeline, _meta = load_pipeline()
    return _pipeline


def _generate_sync(
    prompt: str,
    *,
    aspect: str = "9:16",
    num_frames: int = 81,
    guidance_scale: float = 5.0,
) -> bytes:
    from diffusers.utils import export_to_video

    with _lock:
        pipe = _ensure_pipeline()
        meta = _meta or backend_meta()

    frames, fps = generate_sync(
        pipe,
        meta,
        prompt,
        aspect=aspect,
        num_frames=num_frames,
        guidance_scale=guidance_scale,
    )

    with tempfile.TemporaryDirectory() as tmp:
        out_path = Path(tmp) / "clip.mp4"
        export_to_video(frames, str(out_path), fps=fps)
        return out_path.read_bytes()


async def generate_video_bytes(
    prompt: str,
    *,
    aspect: str = "9:16",
    num_frames: int = 81,
    guidance_scale: float = 5.0,
) -> bytes:
    return await asyncio.to_thread(
        _generate_sync,
        prompt,
        aspect=aspect,
        num_frames=num_frames,
        guidance_scale=guidance_scale,
    )
