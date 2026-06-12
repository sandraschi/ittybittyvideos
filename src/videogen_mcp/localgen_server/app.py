from __future__ import annotations

import os
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field

from videogen_mcp.localgen_server import pipeline as gen_pipeline
from videogen_mcp.localgen_server.backends import BACKENDS


@asynccontextmanager
async def lifespan(app: FastAPI):
    if os.environ.get("LOCALGEN_PRELOAD", os.environ.get("COGVIDEO_PRELOAD", "")).strip().lower() in (
        "1",
        "true",
        "yes",
    ):
        try:
            gen_pipeline.preload_pipeline()
        except Exception as e:
            from loguru import logger

            logger.error(f"LocalGen preload failed: {e}")
    yield


app = FastAPI(title="ittybitty LocalGen", version="0.2.0", lifespan=lifespan)


class GenerateRequest(BaseModel):
    prompt: Annotated[str, Field(min_length=1, max_length=500)]
    aspect: str = "9:16"
    num_frames: int = Field(default=81, ge=16, le=121)
    guidance_scale: float = Field(default=5.0, ge=1.0, le=20.0)


@app.get("/api/health")
async def health():
    info = gen_pipeline.get_runtime_info()
    return {
        "status": "ok",
        "service": "localgen-server",
        "tier": info.tier,
        "backend": info.backend,
        "label": info.label,
        "model_id": info.model_id,
        "model_loaded": gen_pipeline.is_model_loaded(),
        "cuda_available": info.cuda_available,
        "device": info.device,
        "memory_mode": info.memory_mode,
        "deps_installed": info.deps_installed,
        "backends_available": list(BACKENDS.keys()),
        "hint": _health_hint(info),
    }


def _health_hint(info: gen_pipeline.RuntimeInfo) -> str:
    if not info.deps_installed:
        return 'Install 2026 stack: py -m pip install -e ".[localgen]"'
    if info.tier == "legacy":
        return "Legacy CogVideoX backend — set LOCALGEN_BACKEND=wan22-14b for 2026 tier"
    if not info.cuda_available:
        return "No CUDA — Wan 2.2 on CPU is impractical"
    if not gen_pipeline.is_model_loaded():
        return f"Ready; first clip loads {info.label} (~10–40GB download once)"
    return f"{info.label} loaded ({info.memory_mode or 'ready'})"


@app.post("/api/generate")
async def generate(body: GenerateRequest):
    info = gen_pipeline.get_runtime_info()
    if not info.deps_installed:
        raise HTTPException(
            status_code=503,
            detail='LocalGen deps missing. Run: py -m pip install -e ".[localgen]"',
        )
    try:
        video_bytes = await gen_pipeline.generate_video_bytes(
            body.prompt.strip(),
            aspect=body.aspect,
            num_frames=body.num_frames,
            guidance_scale=body.guidance_scale,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

    return Response(content=video_bytes, media_type="video/mp4")


@app.get("/")
async def root():
    return {
        "service": "localgen-server",
        "tier": "2026",
        "default_backend": "wan22-14b",
        "endpoints": ["/api/health", "/api/generate"],
    }
