from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from loguru import logger
from pydantic import Field

from videogen_mcp import __version__
from videogen_mcp.config import get_settings
from videogen_mcp.models.schema import GenerateRequest, JobStatus
from videogen_mcp.models.storyboard import PlanRequest
from videogen_mcp.services.config_store import SettingsUpdate

try:
    from fastmcp import FastMCP
except ImportError:
    FastMCP = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    from videogen_mcp.services.job_store import init_db, scan_output_directory

    init_db()
    imported = scan_output_directory()
    logger.info(f"videogen-mcp v{__version__} starting on port {get_settings().videogen_port}")
    if imported:
        logger.info(f"Depot: imported {imported} video(s) from output folder")
    yield
    logger.info("videogen-mcp shutting down")


rest = FastAPI(
    title="videogen-mcp",
    version=__version__,
    lifespan=lifespan,
)

rest.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


if FastMCP:
    mcp = FastMCP("videogen-mcp")

    @mcp.tool()
    async def videogen_generate(
        topic: Annotated[str, Field(description="Topic or keyword for the video.")] = "",
        script: Annotated[str | None, Field(description="Custom script text (skips LLM).")] = None,
        aspect: Annotated[str, Field(description="Aspect ratio: 9:16, 16:9, or 1:1.")] = "9:16",
        voice: Annotated[str, Field(description="TTS voice identifier.")] = "",
        clip_duration: Annotated[float, Field(description="Seconds per clip.", ge=2.0, le=30.0)] = 5.0,
        paragraph_count: Annotated[int, Field(description="Number of script segments.", ge=1, le=10)] = 3,
        llm_provider: Annotated[
            str, Field(description="Topic LLM: deepseek | openai | lmstudio | ollama (ignored with custom script).")
        ] = "",
    ) -> dict:
        """Generate a short video from a topic or script.

        ## Return Format
        {"success": bool, "job_id": str, "status": str, "message": str}

        ## Examples
        videogen_generate(topic="Why cats are amazing pets")
        videogen_generate(script="The ocean covers 71% of Earth...", aspect="16:9")
        """
        from videogen_mcp.models.schema import VideoAspect
        from videogen_mcp.services.pipeline import generate_video

        req = GenerateRequest(
            topic=topic,
            script=script,
            aspect=VideoAspect(aspect),
            voice=voice,
            clip_duration=clip_duration,
            paragraph_count=paragraph_count,
            llm_provider=llm_provider,
        )
        job = await generate_video(req)
        return {
            "success": True,
            "job_id": job.job_id,
            "status": job.status.value,
            "message": f"Video generation started for: {job.topic}",
        }

    @mcp.tool()
    async def videogen_status(
        job_id: Annotated[str, Field(description="Job ID from videogen_generate.")],
    ) -> dict:
        """Check video generation job progress.

        ## Return Format
        {"success": bool, "job": {job_id, status, progress, output_path, error}}

        ## Examples
        videogen_status(job_id="abc123def456")
        """
        from videogen_mcp.services.pipeline import get_job

        job = get_job(job_id)
        if not job:
            return {"success": False, "message": f"Job {job_id} not found"}
        return {
            "success": True,
            "job": job.model_dump(mode="json"),
        }

    @mcp.tool()
    async def videogen_list_jobs(
        limit: Annotated[int, Field(description="Max jobs to return.", ge=1, le=50)] = 20,
    ) -> dict:
        """List recent video generation jobs.

        ## Return Format
        {"success": bool, "jobs": [{job_id, status, topic, progress}], "count": int}

        ## Examples
        videogen_list_jobs(limit=5)
        """
        from videogen_mcp.services.pipeline import list_jobs

        jobs = list_jobs(limit)
        return {
            "success": True,
            "jobs": [j.model_dump(mode="json") for j in jobs],
            "count": len(jobs),
        }

    @mcp.tool()
    async def videogen_providers() -> dict:
        """List available LLM, stock footage, and TTS providers.

        ## Return Format
        {"success": bool, "providers": {"llm": [...], "stock": [...], "tts": [...]}}

        ## Examples
        videogen_providers()
        """
        from videogen_mcp.providers import list_providers

        return {"success": True, "providers": list_providers()}

    @mcp.tool()
    async def videogen_plan(
        topic: Annotated[str, Field(description="Video topic or subject.")],
        video_type: Annotated[
            str, Field(description="tutorial, demo, explainer, documentary, showcase.")
        ] = "explainer",
        target_duration: Annotated[
            float, Field(description="Target length in seconds (30-900).", ge=30, le=900)
        ] = 300.0,
        language: Annotated[str, Field(description="Language code (en, zh, de, ja).")] = "en",
        chapters: Annotated[int, Field(description="Number of chapters.", ge=1, le=12)] = 4,
        style_notes: Annotated[str, Field(description="Style guidance for the planner.")] = "",
    ) -> dict:
        """Plan an intermediate-length video storyboard with chapters and scenes.

        Uses LLM + videographer rules to produce a coherent multi-scene structure
        with pacing, B-roll, transitions, and chapter markers. Does NOT render --
        use videogen_plan_render to execute.

        ## Return Format
        {"success": bool, "storyboard": {title, chapters, total_scenes, planned_duration}}

        ## Examples
        videogen_plan(topic="How to use Git", video_type="tutorial", target_duration=300)
        videogen_plan(topic="Vienna coffee culture", video_type="documentary", target_duration=600, language="de")
        """
        from videogen_mcp.models.storyboard import PlanRequest, VideoType
        from videogen_mcp.services.planner import plan_video

        req = PlanRequest(
            topic=topic,
            video_type=VideoType(video_type),
            target_duration=target_duration,
            language=language,
            chapters=chapters,
            style_notes=style_notes,
        )
        board = await plan_video(req)
        return {
            "success": True,
            "storyboard": board.model_dump(mode="json"),
            "summary": f"{board.title}: {board.total_scenes} scenes, {len(board.chapters)} chapters, "
            f"{board.planned_duration:.0f}s planned",
        }

    @mcp.tool()
    async def videogen_plan_render(
        topic: Annotated[str, Field(description="Video topic (same as videogen_plan).")],
        video_type: Annotated[
            str, Field(description="tutorial, demo, explainer, documentary, showcase.")
        ] = "explainer",
        target_duration: Annotated[float, Field(description="Target length in seconds.", ge=30, le=900)] = 300.0,
        aspect: Annotated[str, Field(description="Aspect ratio: 9:16, 16:9, 1:1.")] = "16:9",
        language: Annotated[str, Field(description="Language code.")] = "en",
        voice: Annotated[str, Field(description="TTS voice identifier.")] = "",
        chapters: Annotated[int, Field(description="Number of chapters.", ge=1, le=12)] = 4,
    ) -> dict:
        """Plan AND render an intermediate-length video (3-15 min).

        Full pipeline: LLM storyboard -> videographer rules -> scene-by-scene
        footage + TTS + subtitles -> FFmpeg compose -> .mp4

        ## Return Format
        {"success": bool, "job_id": str, "status": str, "message": str}

        ## Examples
        videogen_plan_render(topic="Python asyncio tutorial", target_duration=300, aspect="16:9")
        videogen_plan_render(topic="videogen-mcp demo", video_type="demo", target_duration=180)
        """
        from videogen_mcp.models.schema import VideoAspect
        from videogen_mcp.models.storyboard import PlanRequest, VideoType
        from videogen_mcp.services.pipeline_extended import generate_planned_video

        req = PlanRequest(
            topic=topic,
            video_type=VideoType(video_type),
            target_duration=target_duration,
            language=language,
            chapters=chapters,
        )
        job = await generate_planned_video(req, aspect=VideoAspect(aspect), voice=voice)
        return {
            "success": True,
            "job_id": job.job_id,
            "status": job.status.value,
            "message": f"Planned video generation started for: {topic} ({target_duration / 60:.0f} min)",
        }


_webapp_dir = Path(__file__).resolve().parent.parent.parent / "webapp" / "dist"


@rest.get("/health")
async def health():
    return {"status": "ok", "version": __version__, "service": "videogen-mcp"}


@rest.post("/api/v1/generate")
async def api_generate(request: GenerateRequest):
    from fastapi import HTTPException

    from videogen_mcp.providers.llm_resolve import ensure_llm_for_topic, resolve_llm_for_topic
    from videogen_mcp.services.pipeline import generate_video

    if not request.script and request.topic.strip():
        try:
            if request.llm_provider.strip():
                await ensure_llm_for_topic(request.llm_provider)
            else:
                await resolve_llm_for_topic(None)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e

    job = await generate_video(request)
    return {"success": True, "job_id": job.job_id, "status": job.status.value}


@rest.get("/api/v1/jobs")
async def api_list_jobs(limit: int = 20):
    from videogen_mcp.services.pipeline import list_jobs

    jobs = list_jobs(limit)
    return {"success": True, "jobs": [j.model_dump(mode="json") for j in jobs], "count": len(jobs)}


@rest.get("/api/v1/jobs/{job_id}")
async def api_get_job(job_id: str):
    from videogen_mcp.services.pipeline import get_job

    job = get_job(job_id)
    if not job:
        return {"success": False, "message": f"Job {job_id} not found"}
    return {"success": True, "job": job.model_dump(mode="json")}


@rest.get("/api/v1/jobs/{job_id}/download")
async def api_download(job_id: str):
    from videogen_mcp.services.job_store import resolve_output_path

    path = resolve_output_path(job_id)
    if not path:
        return {"success": False, "message": "Video not ready"}
    return FileResponse(path, filename=f"{job_id}.mp4", media_type="video/mp4")


@rest.get("/api/v1/depot")
async def api_depot(limit: int = 100):
    from videogen_mcp.services.depot import depot_summary, list_depot

    items = list_depot(limit)
    return {
        "success": True,
        "summary": depot_summary().model_dump(),
        "items": [i.model_dump() for i in items],
        "count": len(items),
    }


@rest.post("/api/v1/depot/scan")
async def api_depot_scan():
    from videogen_mcp.services.depot import list_depot, scan_depot

    summary = scan_depot()
    items = list_depot(100)
    return {
        "success": True,
        "summary": summary.model_dump(),
        "items": [i.model_dump() for i in items],
        "message": f"Scan complete; {summary.imported} new import(s)",
    }


@rest.delete("/api/v1/depot/{job_id}")
async def api_depot_delete(job_id: str, delete_file: bool = True):
    from videogen_mcp.services.depot import delete_depot_item

    if delete_depot_item(job_id, delete_file=delete_file):
        return {"success": True, "message": f"Removed {job_id} from depot"}
    return {"success": False, "message": f"Job {job_id} not found"}


@rest.get("/api/v1/depot/{job_id}/poster")
async def api_depot_poster(job_id: str):
    from videogen_mcp.services.depot import ensure_poster

    poster = ensure_poster(job_id)
    if not poster:
        return {"success": False, "message": "Poster unavailable"}
    return FileResponse(poster, media_type="image/jpeg")


@rest.post("/api/v1/plan")
async def api_plan(request: PlanRequest):
    from videogen_mcp.services.planner import plan_video

    board = await plan_video(request)
    return {"success": True, "storyboard": board.model_dump(mode="json")}


@rest.post("/api/v1/plan/render")
async def api_plan_render(
    topic: str,
    video_type: str = "explainer",
    target_duration: float = 300.0,
    aspect: str = "16:9",
    language: str = "en",
    voice: str = "",
    chapters: int = 4,
):
    from videogen_mcp.models.schema import VideoAspect
    from videogen_mcp.models.storyboard import VideoType
    from videogen_mcp.services.pipeline_extended import generate_planned_video

    req = PlanRequest(
        topic=topic,
        video_type=VideoType(video_type),
        target_duration=target_duration,
        language=language,
        chapters=chapters,
    )
    job = await generate_planned_video(req, aspect=VideoAspect(aspect), voice=voice)
    return {"success": True, "job_id": job.job_id, "status": job.status.value}


@rest.get("/api/v1/providers")
async def api_providers():
    from videogen_mcp.providers import list_providers

    return {"success": True, "providers": list_providers()}


@rest.get("/api/v1/status")
async def api_status():
    import shutil

    from videogen_mcp.providers import list_providers
    from videogen_mcp.providers.llm_resolve import llm_topic_status
    from videogen_mcp.services.align import is_available
    from videogen_mcp.services.pipeline import list_jobs
    from videogen_mcp.services.publish import PLATFORMS
    from videogen_mcp.services.stock_status import stock_footage_status

    settings = get_settings()
    jobs = list_jobs(50)
    llm = await llm_topic_status()
    stock = await stock_footage_status()
    complete = sum(1 for j in jobs if j.status == JobStatus.COMPLETE)
    active = sum(1 for j in jobs if j.status not in (JobStatus.COMPLETE, JobStatus.FAILED))

    return {
        "status": "ok",
        "version": __version__,
        "service": "videogen-mcp",
        "product": "roughcutvideos",
        "backend_port": settings.videogen_port,
        "frontend_port": 11055,
        "ffmpeg": shutil.which("ffmpeg") is not None,
        "align_available": is_available(),
        "llm": llm,
        "stock": stock,
        "providers": list_providers(),
        "job_count": len(jobs),
        "jobs_complete": complete,
        "jobs_active": active,
        "publish_platforms": len(PLATFORMS),
        "tool_count": 6 if FastMCP else 0,
    }


@rest.get("/api/v1/settings")
async def api_get_settings():
    from videogen_mcp.services.settings_api import get_settings_with_models

    return await get_settings_with_models()


@rest.get("/api/v1/settings/models")
async def api_list_models(provider: str | None = None):
    from videogen_mcp.services.model_discovery import discover_all_llm_models, discover_llm_models

    if provider:
        result = await discover_llm_models(provider)
        return {"success": True, "discovery": result.model_dump()}
    results = await discover_all_llm_models()
    return {"success": True, "discoveries": [r.model_dump() for r in results]}


@rest.get("/api/v1/settings/stock")
async def api_stock_status():
    from videogen_mcp.services.stock_status import stock_footage_status

    status = await stock_footage_status()
    return {"success": True, "stock": status}


@rest.put("/api/v1/settings")
async def api_save_settings(payload: SettingsUpdate):
    from videogen_mcp.services.settings_api import save_settings

    saved = await save_settings(payload)
    return {"success": True, "settings": saved.model_dump(), "message": "Settings saved to .env"}


@rest.get("/api/v1/tools")
async def api_tools():
    tools = [
        {
            "name": "videogen_generate",
            "description": "Generate a short video (30-60s) from a topic or custom script.",
            "kind": "solo",
        },
        {
            "name": "videogen_plan",
            "description": "Plan a mid-length chaptered storyboard without rendering.",
            "kind": "solo",
        },
        {
            "name": "videogen_plan_render",
            "description": "Plan and render a mid-length video (3-15 min).",
            "kind": "solo",
        },
        {"name": "videogen_status", "description": "Poll job progress.", "kind": "solo"},
        {"name": "videogen_list_jobs", "description": "List recent generation jobs.", "kind": "solo"},
        {"name": "videogen_providers", "description": "List LLM, stock, and TTS providers.", "kind": "solo"},
    ]
    return {"success": True, "tools": tools, "count": len(tools)}


@rest.get("/api/v1/jobs/{job_id}/publish-pack")
async def api_publish_pack(job_id: str):
    from videogen_mcp.services.job_store import get_job, resolve_output_path
    from videogen_mcp.services.publish import build_publish_pack

    job = get_job(job_id)
    if not job:
        return {"success": False, "message": f"Job {job_id} not found"}
    path = resolve_output_path(job_id)
    if path:
        job = job.model_copy(update={"output_path": str(path)})
    return build_publish_pack(job)


@rest.post("/api/v1/jobs/{job_id}/reveal")
async def api_reveal_job(job_id: str):
    import platform
    import subprocess

    from videogen_mcp.services.job_store import resolve_output_path

    path = resolve_output_path(job_id)
    if not path:
        return {"success": False, "message": "Video not ready"}

    if platform.system() == "Windows":
        subprocess.Popen(["explorer", "/select,", str(path.resolve())])  # noqa: S603
        return {"success": True, "message": "Opened Explorer with file selected."}
    return {
        "success": True,
        "message": "Reveal is Windows-only; use download or open path manually.",
        "path": str(path.resolve()),
    }


if _webapp_dir.exists():
    from fastapi.responses import JSONResponse
    from fastapi.staticfiles import StaticFiles

    assets_dir = _webapp_dir / "assets"
    if assets_dir.is_dir():
        rest.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    @rest.get("/")
    async def serve_index():
        return FileResponse(_webapp_dir / "index.html")

    @rest.get("/{spa_path:path}")
    async def spa_fallback(spa_path: str):
        if spa_path.startswith(("api/", "mcp", "docs", "redoc", "openapi.json", "health")):
            return JSONResponse({"success": False, "message": "Not found"}, status_code=404)
        candidate = _webapp_dir / spa_path
        if candidate.is_file():
            return FileResponse(candidate)
        index = _webapp_dir / "index.html"
        if index.is_file():
            return FileResponse(index)
        return JSONResponse({"success": False, "message": "Webapp not built"}, status_code=404)


if FastMCP:
    rest.mount("/mcp", mcp.http_app())

app = rest


def main():
    import uvicorn

    settings = get_settings()
    uvicorn.run(app, host=settings.videogen_host, port=settings.videogen_port)


if __name__ == "__main__":
    main()
