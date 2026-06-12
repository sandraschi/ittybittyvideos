"""Extended pipeline -- executes a Storyboard scene-by-scene into a coherent mid-length video."""

from __future__ import annotations

import asyncio
from pathlib import Path

from loguru import logger

from videogen_mcp.config import get_settings
from videogen_mcp.models.schema import JobInfo, JobStatus, VideoAspect
from videogen_mcp.models.storyboard import PlanRequest, Scene
from videogen_mcp.providers import get_stock, get_tts
from videogen_mcp.providers.base import SubtitleEntry
from videogen_mcp.services import job_store
from videogen_mcp.services.align import align_words, words_to_sentences
from videogen_mcp.services.cache import cache_path, is_cached
from videogen_mcp.services.compose import compose_video
from videogen_mcp.services.critic import critique_video, refetch_queries
from videogen_mcp.services.planner import plan_video


def _save(job: JobInfo) -> None:
    job_store.upsert_job(job)


async def generate_planned_video(
    request: PlanRequest,
    aspect: VideoAspect = VideoAspect.PORTRAIT,
    voice: str = "",
) -> JobInfo:
    job = JobInfo(topic=request.topic)
    _save(job)
    asyncio.create_task(_run_planned_pipeline(job, request, aspect, voice))
    return job


async def _run_planned_pipeline(
    job: JobInfo,
    request: PlanRequest,
    aspect: VideoAspect,
    voice: str,
) -> None:
    settings = get_settings()
    work_dir = settings.videogen_output_dir / job.job_id
    work_dir.mkdir(parents=True, exist_ok=True)

    try:
        job.update(JobStatus.SCRIPTING, 5.0)
        _save(job)
        board = await plan_video(request)
        logger.info(f"[{job.job_id}] Storyboard: {board.title}, {board.total_scenes} scenes")

        all_scenes = board.all_scenes
        total = len(all_scenes)
        scene_footage: list[Path] = []
        scene_audio: list[Path] = []
        scene_subs: list[list[SubtitleEntry]] = []
        scene_words: list[list[SubtitleEntry]] = []
        audio_offset = 0.0

        for i, scene in enumerate(all_scenes):
            progress = 10.0 + (80.0 * i / total)
            job.update(JobStatus.FETCHING_FOOTAGE, progress)
            _save(job)

            footage = await _fetch_scene_footage(scene, aspect, work_dir / f"footage_{i:03d}.mp4")
            scene_footage.append(footage)

            if scene.narration.strip():
                tts = get_tts()
                tts_result = await tts.synthesize(
                    scene.narration,
                    voice,
                    work_dir / f"voice_{i:03d}.mp3",
                )
                scene_audio.append(tts_result.audio_path)

                # R1: word-level timing per scene; whisper-align when provider has none
                words = tts_result.words
                sentences = tts_result.subtitles
                if words is None and settings.videogen_align:
                    words = await asyncio.to_thread(align_words, tts_result.audio_path, scene.narration)
                    if words:
                        sentences = words_to_sentences(words)

                scene_subs.append([_offset(s, audio_offset) for s in sentences])
                scene_words.append([_offset(w, audio_offset) for w in (words or [])])
                audio_offset += tts_result.duration
            else:
                scene_subs.append([])
                scene_words.append([])

        job.update(JobStatus.COMPOSING, 90.0)
        _save(job)

        merged_audio = await _merge_audio(scene_audio, work_dir / "narration_full.mp3")
        all_subs = [s for subs in scene_subs for s in subs]
        all_words = [w for ws in scene_words for w in ws]

        output_path = settings.videogen_output_dir / f"{job.job_id}.mp4"
        clip_dur = max(s.duration_target for s in all_scenes)

        async def _compose() -> None:
            await asyncio.to_thread(
                compose_video,
                footage_paths=scene_footage,
                audio_path=merged_audio,
                subtitles=all_subs,
                output_path=output_path,
                aspect=aspect,
                fps=settings.videogen_default_fps,
                clip_duration=clip_dur,
                word_subtitles=all_words or None,
                sub_style=settings.videogen_sub_style,
            )

        await _compose()

        # R3: Screening Room -- editor watches the dailies, mismatched footage gets re-fetched
        for pass_n in range(1, settings.videogen_screening_passes + 1):
            report = await critique_video(output_path, all_scenes, clip_dur, work_dir, pass_number=pass_n)
            if report is None:
                break
            (work_dir / f"critique_pass_{pass_n}.json").write_text(report.model_dump_json(indent=2), encoding="utf-8")
            queries = refetch_queries(report, all_scenes)
            if not queries:
                logger.info(f"[{job.job_id}] Screening pass {pass_n}: no footage flags, done")
                break
            job.update(JobStatus.COMPOSING, min(99.0, 92.0 + pass_n * 2))
            _save(job)
            replaced = 0
            for idx, query in queries.items():
                try:
                    scene_footage[idx] = await _fetch_scene_footage(
                        all_scenes[idx],
                        aspect,
                        work_dir / f"footage_{idx:03d}_p{pass_n}.mp4",
                        query_override=query,
                        exclude={scene_footage[idx]},
                    )
                    replaced += 1
                except RuntimeError as e:
                    logger.warning(f"[{job.job_id}] Screening: no replacement for scene {idx} ({e})")
            logger.info(f"[{job.job_id}] Screening pass {pass_n}: replaced {replaced}/{len(queries)} flagged clips")
            if replaced:
                await _compose()

        job.output_path = str(output_path)
        job.update(JobStatus.COMPLETE, 100.0)
        _save(job)
        logger.info(f"[{job.job_id}] Complete: {output_path}")

    except Exception as e:
        logger.error(f"[{job.job_id}] Planned pipeline failed: {e}")
        job.error = str(e)
        job.update(JobStatus.FAILED, 0.0)
        _save(job)


def _offset(entry: SubtitleEntry, by: float) -> SubtitleEntry:
    return SubtitleEntry(start=entry.start + by, end=entry.end + by, text=entry.text)


async def _fetch_scene_footage(
    scene: Scene,
    aspect: VideoAspect,
    dest: Path,
    query_override: str | None = None,
    exclude: set[Path] | None = None,
) -> Path:
    if not scene.search_terms:
        scene.search_terms = ["abstract", "cinematic"]

    stock = get_stock()
    query = query_override or " ".join(scene.search_terms[:2])
    clips = await stock.search(query, count=3, aspect=aspect.value)
    excluded = exclude or set()

    for clip in clips:
        cached = is_cached(clip.url)
        if cached:
            if cached in excluded:
                continue
            return cached
        downloaded = await stock.download(clip, cache_path(clip.url))
        if downloaded in excluded:
            continue
        return downloaded

    raise RuntimeError(f"No footage found for scene: {scene.title} ({query})")


async def _merge_audio(audio_paths: list[Path], output: Path) -> Path:
    if not audio_paths:
        raise RuntimeError("No audio segments to merge")
    if len(audio_paths) == 1:
        return audio_paths[0]

    import subprocess
    import tempfile

    list_file = Path(tempfile.mktemp(suffix=".txt"))
    with open(list_file, "w") as f:
        for p in audio_paths:
            f.write(f"file '{p}'\n")

    output.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_file), "-c", "copy", str(output)],
        capture_output=True,
        text=True,
        timeout=120,
    )
    list_file.unlink(missing_ok=True)

    if result.returncode != 0:
        raise RuntimeError(f"Audio merge failed: {result.stderr[-300:]}")
    return output
