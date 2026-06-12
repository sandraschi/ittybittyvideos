"""Screening Room -- closed-loop VLM self-critique (SPEC R3).

An editor watches the dailies: one frame per scene from the rendered
draft goes to a local vision LLM (OpenAI-compatible API, e.g. Ollama
with a Qwen-VL model) together with the scene's narration and metadata.
The VLM returns a structured verdict per scene; footage mismatches are
re-fetched with the critique's fix_hint as the new search query.

Honesty rules:
- VLM unreachable -> critique_video returns None, pipeline ships the
  first render and logs why. Never block a finished video on a critic.
- Unparseable VLM output for a scene -> that scene passes by default
  (a confused critic must not trigger churn), with a warning logged.
"""

from __future__ import annotations

import asyncio
import base64
import json
import re
import subprocess
import tempfile
from pathlib import Path

import httpx
from loguru import logger

from videogen_mcp.config import get_settings
from videogen_mcp.models.critique import CritiqueReport, SceneCritique, SceneIssue
from videogen_mcp.models.storyboard import Scene

_VLM_TIMEOUT = httpx.Timeout(connect=5.0, read=180.0, write=30.0, pool=5.0)

_PROMPT = """You are a strict video editor reviewing one scene of a generated video.

Scene {idx}: "{title}" ({scene_type}, target {duration:.0f}s)
Narration spoken over this footage: "{narration}"

Look at the attached frame. Judge ONLY:
1. footage_mismatch -- does the footage plausibly illustrate the narration?
2. sub_collision -- do burned-in subtitles overlap important image content or each other?
3. weak_hook -- (only if scene_type is 'hook') would this frame stop a scroll?
4. pacing -- does the shot look static/empty enough that {duration:.0f}s on it would drag?

Respond with ONLY a JSON object, no markdown fences, no commentary:
{{"verdict": "pass" or "flag",
"issues": [zero or more of "footage_mismatch","sub_collision","weak_hook","pacing"],
"fix_hint": "if footage_mismatch: a 2-4 word stock search query that WOULD fit, else short editor note"}}"""


def vlm_available() -> bool:
    settings = get_settings()
    try:
        resp = httpx.get(f"{settings.videogen_vlm_url.rstrip('/')}/models", timeout=4.0)
        return resp.status_code == 200
    except Exception:
        return False


def scene_midpoints(n_scenes: int, clip_duration: float) -> list[float]:
    """Sample timestamp per scene: midpoint of its slot in the concat grid."""
    return [i * clip_duration + clip_duration / 2.0 for i in range(n_scenes)]


def extract_frames(video_path: Path, timestamps: list[float], work_dir: Path) -> list[Path | None]:
    """Grab one JPEG per timestamp. None entries mark failed extractions."""
    work_dir.mkdir(parents=True, exist_ok=True)
    frames: list[Path | None] = []
    for i, t in enumerate(timestamps):
        out = work_dir / f"frame_{i:03d}.jpg"
        cmd = ["ffmpeg", "-y", "-ss", f"{t:.2f}", "-i", str(video_path), "-frames:v", "1", "-q:v", "4", str(out)]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0 and out.exists() and out.stat().st_size > 0:
            frames.append(out)
        else:
            logger.warning(f"critic: frame extraction failed at {t:.1f}s")
            frames.append(None)
    return frames


def parse_critique_json(raw: str, scene_index: int) -> SceneCritique:
    """Parse the VLM reply. Unparseable -> default pass (logged)."""
    text = raw.strip()
    text = re.sub(r"^```(?:json)?|```$", "", text, flags=re.MULTILINE).strip()
    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if match:
        text = match.group(0)
    try:
        data = json.loads(text)
        issues = [SceneIssue(i) for i in data.get("issues", []) if i in SceneIssue._value2member_map_]
        verdict = data.get("verdict", "pass")
        if verdict not in ("pass", "flag"):
            verdict = "pass"
        return SceneCritique(
            scene_index=scene_index,
            verdict=verdict,
            issues=issues,
            fix_hint=str(data.get("fix_hint", ""))[:120],
        )
    except (json.JSONDecodeError, ValueError) as e:
        logger.warning(f"critic: unparseable VLM reply for scene {scene_index} ({e}); defaulting to pass")
        return SceneCritique(scene_index=scene_index, verdict="pass")


async def _call_vlm(client: httpx.AsyncClient, frame: Path, prompt: str) -> str:
    settings = get_settings()
    b64 = base64.b64encode(frame.read_bytes()).decode()
    resp = await client.post(
        f"{settings.videogen_vlm_url.rstrip('/')}/chat/completions",
        json={
            "model": settings.videogen_vlm_model,
            "max_tokens": 300,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}},
                    ],
                }
            ],
        },
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


async def critique_video(
    video_path: Path,
    scenes: list[Scene],
    clip_duration: float,
    work_dir: Path,
    pass_number: int = 1,
) -> CritiqueReport | None:
    """Run one screening pass. Returns None when the VLM is unreachable."""
    settings = get_settings()
    if not vlm_available():
        logger.warning(f"critic: VLM at {settings.videogen_vlm_url} unreachable; skipping screening pass")
        return None

    frame_dir = Path(tempfile.mkdtemp(prefix=f"screening_p{pass_number}_", dir=str(work_dir)))
    timestamps = scene_midpoints(len(scenes), clip_duration)
    frames = await asyncio.to_thread(extract_frames, video_path, timestamps, frame_dir)

    critiques: list[SceneCritique] = []
    async with httpx.AsyncClient(timeout=_VLM_TIMEOUT) as client:
        for i, (scene, frame) in enumerate(zip(scenes, frames)):
            if frame is None:
                critiques.append(SceneCritique(scene_index=i, verdict="pass"))
                continue
            prompt = _PROMPT.format(
                idx=i,
                title=scene.title,
                scene_type=scene.scene_type.value,
                duration=scene.duration_target,
                narration=scene.narration[:400],
            )
            try:
                raw = await _call_vlm(client, frame, prompt)
                critiques.append(parse_critique_json(raw, i))
            except Exception as e:
                logger.warning(f"critic: VLM call failed for scene {i} ({e}); defaulting to pass")
                critiques.append(SceneCritique(scene_index=i, verdict="pass"))

    report = CritiqueReport(pass_number=pass_number, model=settings.videogen_vlm_model, scenes=critiques)
    logger.info(
        f"critic: pass {pass_number}: {len(report.flagged)}/{len(scenes)} flagged "
        f"({len(report.footage_flags)} footage)"
    )
    return report


def refetch_queries(report: CritiqueReport, scenes: list[Scene]) -> dict[int, str]:
    """Map flagged scene index -> replacement footage search query."""
    queries: dict[int, str] = {}
    for c in report.footage_flags:
        if 0 <= c.scene_index < len(scenes):
            hint = c.fix_hint.strip()
            queries[c.scene_index] = hint if hint else " ".join(scenes[c.scene_index].search_terms[:3])
    return queries
