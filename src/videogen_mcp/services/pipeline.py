from __future__ import annotations

import asyncio
from pathlib import Path

from loguru import logger

from videogen_mcp.config import get_settings
from videogen_mcp.models.visual_look import apply_visual_look_to_query
from videogen_mcp.models.schema import (
    GenerateRequest,
    JobInfo,
    JobStatus,
    ScriptSegment,
    VideoScript,
)
from videogen_mcp.providers import get_stock, get_tts
from videogen_mcp.providers.llm_resolve import resolve_llm_for_topic
from videogen_mcp.services import job_store
from videogen_mcp.services.align import align_words, words_to_sentences
from videogen_mcp.services.audio import detect_beats, snap_cut_durations
from videogen_mcp.services.cache import cache_path, is_cached
from videogen_mcp.services.compose import compose_video
from videogen_mcp.services.overlay import overlay_talking_head


def get_job(job_id: str) -> JobInfo | None:
    return job_store.get_job(job_id)


def list_jobs(limit: int = 20) -> list[JobInfo]:
    return job_store.list_jobs(limit)


def _save(job: JobInfo) -> None:
    job_store.upsert_job(job)


async def generate_video(request: GenerateRequest) -> JobInfo:
    job = JobInfo(topic=request.topic or "custom script")
    _save(job)
    asyncio.create_task(_run_pipeline(job, request))
    return job


async def _run_pipeline(job: JobInfo, request: GenerateRequest) -> None:
    settings = get_settings()
    output_dir = settings.videogen_output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        job.update(JobStatus.SCRIPTING, 10.0)
        _save(job)
        script = await _get_script(request)
        logger.info(f"[{job.job_id}] Script: {script.title} ({len(script.segments)} segments)")

        job.update(JobStatus.FETCHING_FOOTAGE, 30.0)
        _save(job)
        footage_paths = await _fetch_footage(job.job_id, script, request)
        logger.info(f"[{job.job_id}] Footage: {len(footage_paths)} clips")

        job.update(JobStatus.GENERATING_VOICE, 50.0)
        _save(job)
        full_narration = " ".join(seg.narration for seg in script.segments)
        tts = get_tts()
        audio_dir = output_dir / job.job_id
        audio_dir.mkdir(parents=True, exist_ok=True)
        tts_result = await tts.synthesize(
            full_narration,
            request.voice,
            audio_dir / "narration.mp3",
        )
        logger.info(f"[{job.job_id}] Voice: {tts_result.duration:.1f}s, {len(tts_result.subtitles)} subs")

        words = tts_result.words
        subtitles = tts_result.subtitles
        if words is None and settings.videogen_align:
            words = await asyncio.to_thread(align_words, tts_result.audio_path, full_narration)
            if words:
                subtitles = words_to_sentences(words)

        job.update(JobStatus.COMPOSING, 70.0)
        _save(job)
        output_path = output_dir / f"{job.job_id}.mp4"
        bgm = Path(request.bgm_url) if request.bgm_url else None

        # R2: snap cuts to bgm beats (no-op without bgm or librosa)
        clip_durations = None
        if bgm and bgm.exists() and settings.videogen_beat_snap:
            beats = await asyncio.to_thread(detect_beats, bgm)
            if beats:
                clip_durations = snap_cut_durations(
                    len(footage_paths),
                    request.clip_duration,
                    beats,
                    tolerance=settings.videogen_beat_tolerance,
                )
                logger.info(f"[{job.job_id}] Beat snap: {len(beats)} beats, cuts adjusted")

        await asyncio.to_thread(
            compose_video,
            footage_paths=footage_paths,
            audio_path=tts_result.audio_path,
            subtitles=subtitles,
            output_path=output_path,
            aspect=request.aspect,
            fps=settings.videogen_default_fps,
            clip_duration=request.clip_duration,
            bgm_path=bgm,
            word_subtitles=words,
            sub_style=settings.videogen_sub_style,
            clip_durations=clip_durations,
            duck=settings.videogen_duck,
            duck_ratio=settings.videogen_duck_ratio,
            bgm_volume=settings.videogen_bgm_volume,
        )

        # R9: optional talking-head overlay (separate pass; failure leaves base video intact)
        if settings.videogen_talker_provider and settings.videogen_talker_source:
            job.update(JobStatus.COMPOSING, 90.0)
            _save(job)
            output_path = await _apply_talking_head(job.job_id, output_path, tts_result.audio_path)

        job.output_path = str(output_path)
        job.update(JobStatus.COMPLETE, 100.0)
        _save(job)
        logger.info(f"[{job.job_id}] Complete: {output_path}")

    except Exception as e:
        logger.error(f"[{job.job_id}] Pipeline failed: {e}")
        job.error = str(e)
        job.update(JobStatus.FAILED, 0.0)
        _save(job)


async def _apply_talking_head(job_id: str, video_path: Path, narration_path: Path) -> Path:
    """R9: render a talking head from the narration and overlay it as PiP.

    Any failure logs a warning and returns the un-overlaid video -- a missing
    avatar must never kill a finished render.
    """
    from videogen_mcp.providers import get_talker

    settings = get_settings()
    try:
        talker = get_talker()
        head_path = video_path.parent / f"{job_id}_head.mp4"
        await talker.synthesize_head(narration_path, Path(settings.videogen_talker_source), head_path)
        final = video_path.parent / f"{job_id}_final.mp4"
        await asyncio.to_thread(
            overlay_talking_head,
            video_path,
            head_path,
            final,
            corner=settings.videogen_talker_corner,
            scale=settings.videogen_talker_scale,
        )
        return final
    except Exception as e:
        logger.warning(f"[{job_id}] Talking head skipped: {e}")
        return video_path


async def _get_script(request: GenerateRequest) -> VideoScript:
    if request.script:
        paragraphs = [p.strip() for p in request.script.split("\n\n") if p.strip()]
        segments = [ScriptSegment(narration=p, search_terms=p.split()[:3]) for p in paragraphs]
        return VideoScript(title="Custom Script", segments=segments)

    llm = await resolve_llm_for_topic(request.llm_provider or None)
    raw = await llm.generate_script(request.topic, request.paragraph_count)
    return VideoScript.model_validate(raw)


async def _fetch_footage(job_id: str, script: VideoScript, request: GenerateRequest) -> list[Path]:
    stock = get_stock()
    stock_name = get_settings().videogen_stock_provider
    look = request.visual_look()
    all_paths: list[Path] = []
    seen_sources: set[str] = set()

    for segment in script.segments:
        query = apply_visual_look_to_query(" ".join(segment.search_terms[:2]), look, stock_name)
        clips = await stock.search(query, count=3, aspect=request.aspect.value)

        for clip in clips:
            if clip.source in seen_sources:
                continue
            seen_sources.add(clip.source)

            cached = is_cached(clip.url)
            if cached:
                all_paths.append(cached)
            else:
                dest = cache_path(clip.url)
                downloaded = await stock.download(clip, dest)
                all_paths.append(downloaded)

            if len(all_paths) >= request.paragraph_count * 2:
                break

        if len(all_paths) >= request.paragraph_count * 2:
            break

    if not all_paths:
        raise RuntimeError("No footage clips found for any search term")
    return all_paths
