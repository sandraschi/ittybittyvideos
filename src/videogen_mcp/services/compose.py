from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

from loguru import logger

from videogen_mcp.models.schema import VideoAspect
from videogen_mcp.providers.base import SubtitleEntry


def compose_video(
    footage_paths: list[Path],
    audio_path: Path,
    subtitles: list[SubtitleEntry],
    output_path: Path,
    aspect: VideoAspect = VideoAspect.PORTRAIT,
    fps: int = 30,
    clip_duration: float = 5.0,
    bgm_path: Path | None = None,
) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    w, h = aspect.resolution

    concat_file = _build_concat_file(footage_paths, clip_duration)
    srt_file = _build_srt(subtitles)

    cmd = [
        "ffmpeg",
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(concat_file),
        "-i",
        str(audio_path),
    ]

    filter_parts = [f"[0:v]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},setsar=1,fps={fps}[scaled]"]

    if srt_file:
        cmd.extend(["-i", str(srt_file)])
        filter_parts.append(
            f"[scaled]subtitles='{_escape_filter_path(srt_file)}':"
            f"force_style='FontSize=14,PrimaryColour=&H00FFFFFF,"
            f"OutlineColour=&H00000000,Outline=2,Alignment=2,"
            f"MarginV=40'[out]"
        )
    else:
        filter_parts.append("[scaled]copy[out]")

    audio_filter = "[1:a]aresample=44100[aout]"
    if bgm_path and bgm_path.exists():
        cmd.extend(["-i", str(bgm_path)])
        bgm_idx = 3 if srt_file else 2
        audio_filter = (
            f"[1:a]aresample=44100,volume=1.0[voice];"
            f"[{bgm_idx}:a]aresample=44100,volume=0.15[bgm];"
            f"[voice][bgm]amix=inputs=2:duration=first[aout]"
        )

    full_filter = ";".join(filter_parts) + ";" + audio_filter
    cmd.extend(
        [
            "-filter_complex",
            full_filter,
            "-map",
            "[out]",
            "-map",
            "[aout]",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "23",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-shortest",
            "-movflags",
            "+faststart",
            str(output_path),
        ]
    )

    logger.info(f"FFmpeg compose: {len(footage_paths)} clips -> {output_path.name}")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if result.returncode != 0:
        logger.error(f"FFmpeg failed: {result.stderr[-500:]}")
        raise RuntimeError(f"FFmpeg compose failed: {result.stderr[-300:]}")

    _cleanup_temp(concat_file, srt_file)
    logger.info(f"Video composed: {output_path} ({output_path.stat().st_size / 1024 / 1024:.1f} MB)")
    return output_path


def _build_concat_file(paths: list[Path], clip_duration: float) -> Path:
    tmp = Path(tempfile.mktemp(suffix=".txt"))
    with open(tmp, "w") as f:
        for p in paths:
            f.write(f"file '{p}'\n")
            f.write("inpoint 0\n")
            f.write(f"outpoint {clip_duration}\n")
    return tmp


def _build_srt(subtitles: list[SubtitleEntry]) -> Path | None:
    if not subtitles:
        return None
    tmp = Path(tempfile.mktemp(suffix=".srt"))
    with open(tmp, "w", encoding="utf-8") as f:
        for i, sub in enumerate(subtitles, 1):
            f.write(f"{i}\n")
            f.write(f"{_format_time(sub.start)} --> {_format_time(sub.end)}\n")
            f.write(f"{sub.text}\n\n")
    return tmp


def _format_time(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def _escape_filter_path(p: Path) -> str:
    return str(p).replace("\\", "/").replace(":", "\\:")


def _cleanup_temp(*paths: Path | None) -> None:
    for p in paths:
        if p and p.exists():
            try:
                p.unlink()
            except OSError:
                pass
