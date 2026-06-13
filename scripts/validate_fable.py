"""One-shot live validation for R1 (alignment/karaoke), R2 (beats/duck), R3 (screening).

Named after Fable 5 (Anthropic frontier review agent) — not a videogen provider.
See mcp-central-docs/adn-notes/ADN-2026-06-12-001-ittybitty-fable5-live-validation.md.

Run: uv run python scripts/validate_fable.py
Writes findings to stdout; artifacts land in ./output as normal jobs.
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
import time
from pathlib import Path

BGM = Path(r"d:\dev\repos\temp\validate_bgm_120bpm.mp3")

os.environ["VIDEOGEN_SUB_STYLE"] = "karaoke"
os.environ["VIDEOGEN_VLM_URL"] = "http://localhost:11434/v1"
os.environ["VIDEOGEN_VLM_MODEL"] = "gemma4:e4b"  # 26b doesn't fit 24GB VRAM with vision tower
os.environ["VIDEOGEN_SCREENING_PASSES"] = "1"
os.environ["VIDEOGEN_WHISPER_DEVICE"] = "cpu"  # cublas64_12 absent; auto's cuda-fail-retry path can wedge in threads

from videogen_mcp.config import get_settings  # noqa: E402

get_settings.cache_clear()

from videogen_mcp.models.schema import GenerateRequest, JobInfo, JobStatus, VideoAspect  # noqa: E402
from videogen_mcp.services.job_store import init_db  # noqa: E402


def banner(s: str) -> None:
    print(f"\n{'=' * 60}\n{s}\n{'=' * 60}", flush=True)


async def phase1_short() -> bool:
    """R1 + R2: custom script (no LLM), Pexels footage, BGM, karaoke subs."""
    from videogen_mcp.services.pipeline import _run_pipeline

    banner("PHASE 1: short pipeline (R1 alignment+karaoke, R2 beats+duck)")
    script = (
        "Vienna coffee houses are living rooms for people who think. "
        "Marble tables, bentwood chairs, and a waiter who ignores you politely.\n\n"
        "Steaming espresso cups arrive on silver trays with a glass of water. "
        "Nobody hurries, and the newspapers hang on wooden racks.\n\n"
        "Old library books and velvet benches complete the scene. "
        "You pay for the chair, the coffee is incidental."
    )
    req = GenerateRequest(
        topic="",
        script=script,
        aspect=VideoAspect.PORTRAIT,
        voice="",
        clip_duration=5.0,
        paragraph_count=3,
        bgm_url=str(BGM),
    )
    job = JobInfo(topic="fable-validation-short")
    t0 = time.time()
    await _run_pipeline(job, req)
    dt = time.time() - t0
    print(f"phase1: status={job.status.value} in {dt:.0f}s, output={job.output_path}, error={job.error}", flush=True)
    if job.status != JobStatus.COMPLETE:
        return False
    out = Path(job.output_path)
    print(f"phase1: file {out.stat().st_size / 1024 / 1024:.1f} MB", flush=True)
    return True


async def phase2_screening() -> bool:
    """R3: tiny plan_render with one screening pass against gemma4:26b."""
    from videogen_mcp.models.storyboard import PlanRequest, VideoType
    from videogen_mcp.services.critic import vlm_available
    from videogen_mcp.services.pipeline_extended import _run_planned_pipeline

    banner("PHASE 2: mid-length pipeline (R3 screening)")
    if not vlm_available():
        print("phase2: VLM unreachable at startup -- screening would be skipped; ABORT phase 2", flush=True)
        return False

    req = PlanRequest(
        topic="Why dogs tilt their heads",
        video_type=VideoType.EXPLAINER,
        target_duration=60.0,
        chapters=2,
    )
    job = JobInfo(topic="fable-validation-screening")
    t0 = time.time()
    await _run_planned_pipeline(job, req, VideoAspect.LANDSCAPE, "")
    dt = time.time() - t0
    print(f"phase2: status={job.status.value} in {dt:.0f}s, output={job.output_path}, error={job.error}", flush=True)
    if job.status != JobStatus.COMPLETE:
        return False

    work_dir = get_settings().videogen_output_dir / job.job_id
    critiques = sorted(work_dir.glob("critique_pass_*.json"))
    if not critiques:
        print("phase2: NO critique JSON written (screening skipped?)", flush=True)
        return False
    for c in critiques:
        data = json.loads(c.read_text(encoding="utf-8"))
        flags = [s for s in data["scenes"] if s["verdict"] == "flag"]
        print(f"phase2: {c.name}: model={data['model']}, {len(data['scenes'])} scenes, {len(flags)} flagged", flush=True)
        for s in flags:
            print(f"  - scene {s['scene_index']}: {s['issues']} hint={s['fix_hint']!r}", flush=True)
    return True


async def main() -> int:
    init_db()
    if not BGM.exists():
        print(f"BGM track missing: {BGM}", flush=True)
        return 1
    phase2_only = "--phase2" in sys.argv
    ok1 = True if phase2_only else await phase1_short()
    ok2 = await phase2_screening()
    banner(f"RESULT: phase1={'OK' if ok1 else 'FAIL'} phase2={'OK' if ok2 else 'FAIL'}")
    return 0 if (ok1 and ok2) else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
