from __future__ import annotations

import os
from typing import Any

from loguru import logger

from videogen_mcp.localgen_server.backends import BACKENDS, DEFAULT_BACKEND, WAN_NEGATIVE_PROMPT


def resolve_backend_key() -> str:
    key = os.environ.get("LOCALGEN_BACKEND", DEFAULT_BACKEND).strip().lower()
    if key in BACKENDS:
        return key
    # Allow passing a full HF model id
    for k, meta in BACKENDS.items():
        if meta["model_id"].lower() == key.lower():
            return k
    logger.warning(f"Unknown LOCALGEN_BACKEND={key!r}, falling back to {DEFAULT_BACKEND}")
    return DEFAULT_BACKEND


def backend_meta(key: str | None = None) -> dict[str, str]:
    k = key or resolve_backend_key()
    return BACKENDS[k]


def _resolution_for_aspect(aspect: str) -> tuple[int, int]:
    """Wan 2.2 native 720p family; compose.py crops to final 9:16 export."""
    mapping = {
        "9:16": (720, 1280),
        "16:9": (1280, 720),
        "1:1": (720, 720),
    }
    return mapping.get(aspect, (1280, 720))


def _configure_memory(pipe: Any, *, model_id: str) -> str:
    import torch

    if not torch.cuda.is_available():
        pipe.enable_sequential_cpu_offload()
        return "cpu-offload"

    vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
    mid = model_id.lower()
    if "14b" in mid or "a14b" in mid:
        # 4090: MoE 14B fits with offload; full GPU often OOM
        if hasattr(pipe, "enable_model_cpu_offload"):
            pipe.enable_model_cpu_offload()
        else:
            pipe.enable_sequential_cpu_offload()
        return f"model-cpu-offload ({vram_gb:.0f}GB VRAM)"
    if vram_gb >= 14:
        pipe.to("cuda")
        return f"cuda ({vram_gb:.0f}GB VRAM)"
    pipe.enable_model_cpu_offload()
    return f"model-cpu-offload ({vram_gb:.0f}GB VRAM)"


def load_pipeline(model_id: str | None = None) -> tuple[Any, dict[str, str]]:
    import torch

    key = resolve_backend_key()
    meta = BACKENDS[key]
    model_id = model_id or os.environ.get("LOCALGEN_MODEL") or meta["model_id"]

    if "cogvideo" in key or "CogVideoX" in model_id:
        return _load_cogvideo(model_id), {**meta, "model_id": model_id, "backend": key}

    try:
        from diffusers import AutoencoderKLWan, WanPipeline
    except ImportError as e:
        raise RuntimeError('Wan 2.2 needs diffusers main branch. Install: py -m pip install -e ".[localgen]"') from e

    logger.info(f"Loading Wan pipeline: {model_id}")
    vae = AutoencoderKLWan.from_pretrained(model_id, subfolder="vae", torch_dtype=torch.float32)
    pipe = WanPipeline.from_pretrained(model_id, vae=vae, torch_dtype=torch.bfloat16)
    mode = _configure_memory(pipe, model_id=model_id)
    logger.info(f"Wan ready — {mode}")
    return pipe, {**meta, "model_id": model_id, "backend": key, "memory_mode": mode}


def _load_cogvideo(model_id: str) -> Any:
    import torch
    from diffusers import CogVideoXDDIMScheduler, CogVideoXPipeline

    pipe = CogVideoXPipeline.from_pretrained(model_id, torch_dtype=torch.float16)
    pipe.scheduler = CogVideoXDDIMScheduler.from_config(pipe.scheduler.config, timestep_spacing="trailing")
    _configure_memory(pipe, model_id=model_id)
    return pipe


def generate_sync(
    pipe: Any,
    meta: dict[str, str],
    prompt: str,
    *,
    aspect: str = "9:16",
    num_frames: int | None = None,
    guidance_scale: float = 5.0,
    num_inference_steps: int | None = None,
    seed: int | None = None,
) -> tuple[Any, int]:
    import torch

    width, height = _resolution_for_aspect(aspect)
    frames = num_frames or int(os.environ.get("LOCALGEN_FRAMES", meta.get("default_frames", "81")))
    steps = num_inference_steps or int(os.environ.get("LOCALGEN_STEPS", meta.get("default_steps", "40")))
    if os.environ.get("LOCALGEN_FAST", "").strip().lower() in ("1", "true", "yes"):
        steps = min(steps, 25)
        frames = min(frames, 49)

    gen = torch.Generator(device="cuda" if torch.cuda.is_available() else "cpu")
    if seed is not None:
        gen.manual_seed(seed)
    elif os.environ.get("LOCALGEN_SEED"):
        gen.manual_seed(int(os.environ["LOCALGEN_SEED"]))

    backend = meta.get("backend", "")
    logger.info(f"LocalGen [{meta.get('label')}]: {prompt[:60]!r} {width}x{height} frames={frames} steps={steps}")

    if backend.startswith("cogvideo") or "CogVideoX" in meta.get("model_id", ""):
        result = pipe(
            prompt=prompt,
            width=720,
            height=480,
            num_videos_per_prompt=1,
            num_inference_steps=steps,
            num_frames=frames,
            guidance_scale=guidance_scale,
            generator=gen,
        )
        fps = int(meta.get("fps", "8"))
        return result.frames[0], fps

    kwargs: dict[str, Any] = {
        "prompt": prompt,
        "negative_prompt": WAN_NEGATIVE_PROMPT,
        "width": width,
        "height": height,
        "num_frames": frames,
        "guidance_scale": guidance_scale,
        "num_inference_steps": steps,
        "generator": gen,
    }
    if "14b" in backend or "a14b" in meta.get("model_id", "").lower():
        kwargs["guidance_scale"] = 4.0
        kwargs["guidance_scale_2"] = 3.0

    output = pipe(**kwargs).frames[0]
    fps = int(os.environ.get("LOCALGEN_FPS", meta.get("fps", "16")))
    return output, fps
