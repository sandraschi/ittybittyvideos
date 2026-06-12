"""Stock footage provider readiness (Pexels cloud vs LocalGen / Wan 2.2)."""

from __future__ import annotations

from videogen_mcp.config import get_settings


async def stock_footage_status() -> dict:
    settings = get_settings()
    pexels_ready = bool(settings.pexels_api_key.strip())
    cogvideo_ready = False
    cogvideo_error = ""
    cogvideo_model = ""
    cogvideo_hint = ""

    if settings.cogvideo_url.strip():
        try:
            import httpx

            base = settings.cogvideo_url.rstrip("/")
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get(f"{base}/api/health")
                if resp.status_code == 200:
                    cogvideo_ready = True
                    body = resp.json()
                    cogvideo_model = str(body.get("model_id", ""))
                    cogvideo_hint = str(body.get("hint", ""))
                    if not body.get("deps_installed", True):
                        cogvideo_ready = False
                        cogvideo_error = body.get("hint") or "CogVideoX dependencies not installed on server"
                else:
                    cogvideo_error = f"HTTP {resp.status_code} from {base}/api/health"
        except Exception as e:
            cogvideo_error = str(e)

    active = settings.videogen_stock_provider
    ready_for_renders = (active == "pexels" and pexels_ready) or (
        active in ("localgen", "cogvideo") and cogvideo_ready
    )

    hint = "Pexels API key required for stock footage."
    if active in ("localgen", "cogvideo"):
        hint = (
            "LocalGen sidecar required (Wan 2.2 default). Start start-localgen.bat on RTX 4090. "
            "Hybrid Pexels+fallback ships later."
        )
        if cogvideo_ready:
            tier = cogvideo_hint or cogvideo_model or "Wan 2.2"
            hint = f"LocalGen ready ({tier}); ~5s clips at 720p/24fps."
        elif not settings.cogvideo_url.strip():
            hint = "Set COGVIDEO_URL or LOCALGEN_URL (default http://localhost:8188)."

    return {
        "active_provider": active,
        "ready_for_renders": ready_for_renders,
        "pexels_ready": pexels_ready,
        "cogvideo_url": settings.cogvideo_url,
        "cogvideo_ready": cogvideo_ready,
        "cogvideo_error": cogvideo_error,
        "cogvideo_model": cogvideo_model,
        "cogvideo_server_hint": cogvideo_hint,
        "hint": hint,
    }
