"""Google cloud video generation — Veo and Gemini Omni.

Primary path: HTTP bridge to fleet ``google-ai-mcp`` (``GOOGLE_AI_MCP_URL``, port 11014).
Fallback: direct ``google-genai`` when ``pip install -e \".[google]\"`` and credentials set.
"""

from __future__ import annotations

import asyncio
import base64
import uuid
from pathlib import Path
from typing import Any, Literal
from urllib.parse import parse_qs, quote, unquote, urlparse

import httpx

from videogen_mcp.config import get_settings

GoogleBackend = Literal["veo", "omni"]

DEFAULT_VEO_MODEL = "veo-3.1-preview-002"
DEFAULT_OMNI_MODEL = "gemini-omni-flash"
VEO_DURATION_RANGE = (5, 8)
OMNI_DURATION_RANGE = (1, 10)


def _aspect_to_ratio(aspect: str) -> str:
    if aspect in ("9:16", "16:9", "1:1"):
        return aspect
    return "9:16"


def _clip_duration(backend: GoogleBackend, requested: float) -> int:
    lo, hi = VEO_DURATION_RANGE if backend == "veo" else OMNI_DURATION_RANGE
    return max(lo, min(hi, int(round(requested or lo))))


def prompt_from_google_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme in ("veo", "omni"):
        qs = parse_qs(parsed.query)
        if qs.get("prompt"):
            return unquote(qs["prompt"][0])
    if "prompt=" in url:
        return unquote(url.split("prompt=", 1)[1].split("&", 1)[0])
    return "cinematic scene"


def aspect_from_google_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme in ("veo", "omni"):
        qs = parse_qs(parsed.query)
        if qs.get("aspect"):
            return qs["aspect"][0]
    if "aspect=" in url:
        return url.split("aspect=", 1)[1].split("&", 1)[0]
    return "9:16"


def google_clip_url(backend: GoogleBackend, query: str, aspect: str) -> str:
    prompt = quote(query, safe="")
    return f"{backend}://generate?prompt={prompt}&aspect={aspect}"


def google_credentials_configured() -> bool:
    settings = get_settings()
    return bool(
        settings.google_ai_mcp_url.strip() or settings.google_api_key.strip() or settings.google_cloud_project.strip()
    )


async def probe_google_bridge() -> tuple[bool, str]:
    settings = get_settings()
    base = settings.google_ai_mcp_url.strip().rstrip("/")
    if not base:
        return False, ""
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(f"{base}/api/health")
            if resp.status_code != 200:
                return False, f"google-ai-mcp health HTTP {resp.status_code}"
            body = resp.json()
            if body.get("status") == "ok":
                return True, "google-ai-mcp reachable"
            return False, "google-ai-mcp health check failed"
    except Exception as e:
        return False, str(e)


async def google_backend_status(backend: GoogleBackend) -> dict[str, Any]:
    settings = get_settings()
    bridge_ok, bridge_msg = await probe_google_bridge()
    creds = google_credentials_configured()

    if bridge_ok:
        ready = True
        hint = f"Via google-ai-mcp at {settings.google_ai_mcp_url.rstrip('/')}"
        if backend == "veo":
            hint += " — Veo 3.x clips (~5–8 s)."
        else:
            hint += " — Gemini Omni Flash (~10 s, multimodal)."
    elif creds and backend == "omni":
        ready = _omni_direct_available()
        hint = (
            'Direct Gemini Omni (google-genai). Install: pip install -e ".[google]".'
            if not ready
            else "Direct Gemini Omni ready."
        )
    elif creds and backend == "veo":
        ready = _veo_direct_available()
        hint = (
            'Direct Veo needs GOOGLE_CLOUD_PROJECT + pip install -e ".[google]".'
            if not ready
            else "Direct Veo (Vertex) ready."
        )
    else:
        ready = False
        hint = (
            "Set GOOGLE_AI_MCP_URL (http://127.0.0.1:11014) or GOOGLE_API_KEY / "
            "GOOGLE_CLOUD_PROJECT for cloud AI footage."
        )

    return {
        "ready": ready,
        "bridge_ok": bridge_ok,
        "bridge_message": bridge_msg,
        "credentials_configured": creds,
        "hint": hint,
        "google_ai_mcp_url": settings.google_ai_mcp_url,
    }


def _omni_direct_available() -> bool:
    try:
        from google import genai  # noqa: F401

        return google_credentials_configured()
    except ImportError:
        return False


def _veo_direct_available() -> bool:
    settings = get_settings()
    if not settings.google_cloud_project.strip():
        return False
    try:
        import vertexai  # noqa: F401

        return True
    except ImportError:
        return False


async def generate_google_clip(
    backend: GoogleBackend,
    prompt: str,
    aspect: str,
    dest: Path,
    duration_seconds: float = 6.0,
) -> Path:
    settings = get_settings()
    dest.parent.mkdir(parents=True, exist_ok=True)
    duration = _clip_duration(backend, duration_seconds)
    aspect_ratio = _aspect_to_ratio(aspect)

    if settings.google_ai_mcp_url.strip():
        return await _generate_via_bridge(backend, prompt, aspect_ratio, duration, dest)

    if backend == "veo":
        return await _generate_veo_direct(prompt, aspect_ratio, duration, dest)
    return await _generate_omni_direct(prompt, aspect_ratio, duration, dest)


async def _generate_via_bridge(
    backend: GoogleBackend,
    prompt: str,
    aspect_ratio: str,
    duration: int,
    dest: Path,
) -> Path:
    settings = get_settings()
    base = settings.google_ai_mcp_url.strip().rstrip("/")

    if backend == "veo":
        path = "/api/v1/generate_video"
        payload = {
            "prompt": prompt,
            "model": settings.google_veo_model or DEFAULT_VEO_MODEL,
            "duration": duration,
            "aspect_ratio": aspect_ratio,
            "num_videos": 1,
        }
    else:
        path = "/api/v1/omni/generate"
        payload = {
            "prompt": prompt,
            "model": settings.google_omni_model or DEFAULT_OMNI_MODEL,
            "duration": duration,
            "aspect_ratio": aspect_ratio,
            "num_outputs": 1,
        }

    async with httpx.AsyncClient(timeout=600) as client:
        resp = await client.post(f"{base}{path}", json=payload)
        resp.raise_for_status()
        data = resp.json()

    if not data.get("success"):
        raise RuntimeError(data.get("error") or data.get("message") or "Google video generation failed")

    if data.get("mock_mode"):
        raise RuntimeError(
            "google-ai-mcp returned mock output — set GOOGLE_API_KEY or GOOGLE_CLOUD_PROJECT in google-ai-mcp settings."
        )

    return _copy_result_to_dest(data, backend, dest)


def _copy_result_to_dest(data: dict[str, Any], backend: GoogleBackend, dest: Path) -> Path:
    items = data.get("videos") if backend == "veo" else data.get("outputs")
    if not items:
        raise RuntimeError("No video returned from Google generation")

    item = items[0]
    local_path = item.get("local_path")
    if local_path:
        src = Path(local_path)
        if src.is_file():
            if src.stat().st_size < 1024 and src.read_bytes()[:4] != b"\x00\x00\x00\x18":
                text_head = src.read_text(encoding="utf-8", errors="ignore")[:80]
                if "Mock" in text_head or "placeholder" in text_head.lower():
                    raise RuntimeError("Google returned a mock placeholder file, not video bytes")
            dest.write_bytes(src.read_bytes())
            return dest

    raise RuntimeError("Google video path missing or unreadable — is google-ai-mcp on the same machine?")


async def _generate_veo_direct(prompt: str, aspect_ratio: str, duration: int, dest: Path) -> Path:
    settings = get_settings()
    if not settings.google_cloud_project.strip():
        raise RuntimeError("GOOGLE_CLOUD_PROJECT required for direct Veo (or set GOOGLE_AI_MCP_URL).")

    try:
        import vertexai
        from google.cloud import aiplatform
        from google.cloud.aiplatform_v1 import PredictionServiceClient
        from google.protobuf import json_format
    except ImportError as e:
        raise RuntimeError('Install direct Google deps: pip install -e ".[google]"') from e

    location = settings.google_cloud_location or "us-central1"
    model = settings.google_veo_model or DEFAULT_VEO_MODEL

    def _execute():
        vertexai.init(project=settings.google_cloud_project, location=location)
        aiplatform.init(project=settings.google_cloud_project, location=location)
        endpoint = f"projects/{settings.google_cloud_project}/locations/{location}/publishers/google/models/{model}"
        client = PredictionServiceClient(client_options={"api_endpoint": f"{location}-aiplatform.googleapis.com"})
        request_payload = {
            "instances": [{"prompt": prompt}],
            "parameters": {
                "sampleCount": 1,
                "aspectRatio": aspect_ratio,
                "durationSeconds": duration,
                "personGeneration": "allow_adult",
                "safetyFilterLevel": "block_some",
            },
        }
        return client.predict(
            endpoint=endpoint,
            instances=[json_format.ParseDict(inst, aiplatform.types.Value()) for inst in request_payload["instances"]],
            parameters=json_format.ParseDict(request_payload["parameters"], aiplatform.types.Value()),
        )

    response = await asyncio.to_thread(_execute)
    for prediction in response.predictions:
        pred_dict = json_format.MessageToDict(prediction)
        video_data = pred_dict.get("videoBytes") or pred_dict.get("video", {}).get("data")
        if video_data:
            dest.write_bytes(base64.b64decode(video_data))
            return dest

    raise RuntimeError("Veo returned no video data — check project access and model availability.")


async def _generate_omni_direct(prompt: str, aspect_ratio: str, duration: int, dest: Path) -> Path:
    settings = get_settings()
    try:
        from google import genai
        from google.genai import types
    except ImportError as e:
        raise RuntimeError('Install direct Google deps: pip install -e ".[google]"') from e

    if settings.google_cloud_project.strip():
        client = genai.Client(
            vertexai=True,
            project=settings.google_cloud_project,
            location=settings.google_cloud_location or "us-central1",
        )
    elif settings.google_api_key.strip():
        client = genai.Client(api_key=settings.google_api_key)
    else:
        raise RuntimeError("GOOGLE_API_KEY or GOOGLE_CLOUD_PROJECT required for Omni (or set GOOGLE_AI_MCP_URL).")

    model = settings.google_omni_model or DEFAULT_OMNI_MODEL
    config = types.GenerateContentConfig(
        response_modalities=["VIDEO"],
        video_config=types.VideoConfig(duration_seconds=duration, aspect_ratio=aspect_ratio),
    )

    def _call():
        return client.models.generate_content(model=model, contents=[prompt], config=config)

    response = await asyncio.to_thread(_call)
    tmp_dir = dest.parent / f"_omni_{uuid.uuid4().hex[:8]}"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    try:
        for candidate in getattr(response, "candidates", None) or []:
            content = getattr(candidate, "content", None)
            if not content:
                continue
            for part in getattr(content, "parts", []) or []:
                inline = getattr(part, "inline_data", None)
                if inline and getattr(inline, "data", None):
                    data = inline.data
                    raw = base64.b64decode(data) if isinstance(data, str) else data
                    dest.write_bytes(raw)
                    return dest
    finally:
        if tmp_dir.exists() and not any(tmp_dir.iterdir()):
            tmp_dir.rmdir()

    raise RuntimeError("Gemini Omni returned no video — API may not be GA in your region yet.")
