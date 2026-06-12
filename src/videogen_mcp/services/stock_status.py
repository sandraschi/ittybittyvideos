"""Stock footage provider readiness (Pexels, LocalGen, Google Veo/Omni)."""

from __future__ import annotations

from videogen_mcp.config import get_settings
from videogen_mcp.services.google_video import google_backend_status


async def stock_footage_status() -> dict:
    settings = get_settings()
    pexels_ready = bool(settings.pexels_api_key.strip())
    cogvideo_ready = False
    cogvideo_error = ""
    cogvideo_model = ""
    cogvideo_hint = ""

    localgen_base = (settings.localgen_url or settings.cogvideo_url).strip()
    if localgen_base:
        try:
            import httpx

            base = localgen_base.rstrip("/")
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get(f"{base}/api/health")
                if resp.status_code == 200:
                    cogvideo_ready = True
                    body = resp.json()
                    cogvideo_model = str(body.get("model_id", ""))
                    cogvideo_hint = str(body.get("hint", ""))
                    if not body.get("deps_installed", True):
                        cogvideo_ready = False
                        cogvideo_error = body.get("hint") or "LocalGen dependencies not installed on server"
                else:
                    cogvideo_error = f"HTTP {resp.status_code} from {base}/api/health"
        except Exception as e:
            cogvideo_error = str(e)

    veo_status = await google_backend_status("veo")
    omni_status = await google_backend_status("omni")

    active = settings.videogen_stock_provider
    ready_for_renders = (active == "pexels" and pexels_ready) or (
        active in ("localgen", "cogvideo") and cogvideo_ready
    ) or (active == "veo" and veo_status["ready"]) or (active == "omni" and omni_status["ready"])

    hint = "Pexels API key required for stock footage."
    if active in ("localgen", "cogvideo"):
        hint = (
            "LocalGen sidecar required (Wan 2.2 default). Start start-localgen.bat on RTX 4090. "
            "Hybrid Pexels+fallback ships later."
        )
        if cogvideo_ready:
            tier = cogvideo_hint or cogvideo_model or "Wan 2.2"
            hint = f"LocalGen ready ({tier}); ~5s clips at 720p/24fps."
        elif not localgen_base:
            hint = "Set COGVIDEO_URL or LOCALGEN_URL (default http://localhost:8188)."
    elif active == "veo":
        hint = str(veo_status["hint"])
    elif active == "omni":
        hint = str(omni_status["hint"])

    return {
        "active_provider": active,
        "ready_for_renders": ready_for_renders,
        "pexels_ready": pexels_ready,
        "cogvideo_url": settings.cogvideo_url,
        "localgen_url": localgen_base,
        "cogvideo_ready": cogvideo_ready,
        "cogvideo_error": cogvideo_error,
        "cogvideo_model": cogvideo_model,
        "cogvideo_server_hint": cogvideo_hint,
        "veo_ready": veo_status["ready"],
        "veo_hint": veo_status["hint"],
        "veo_bridge_ok": veo_status["bridge_ok"],
        "omni_ready": omni_status["ready"],
        "omni_hint": omni_status["hint"],
        "omni_bridge_ok": omni_status["bridge_ok"],
        "google_ai_mcp_url": settings.google_ai_mcp_url,
        "google_configured": veo_status["credentials_configured"],
        "hint": hint,
    }
