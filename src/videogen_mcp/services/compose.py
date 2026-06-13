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
    word_subtitles: list[SubtitleEntry] | None = None,
    sub_style: str = "sentence",
    clip_durations: list[float] | None = None,
    duck: bool = True,
    duck_ratio: float = 8.0,
    bgm_volume: float = 0.3,
) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    w, h = aspect.resolution

    concat_file = _build_concat_file(footage_paths, clip_duration, clip_durations)

    use_karaoke = sub_style == "karaoke" and bool(word_subtitles)
    if sub_style == "karaoke" and not word_subtitles:
        logger.warning("compose: karaoke style requested but no word timestamps available; using sentence subs")
    sub_file = _build_ass_karaoke(word_subtitles, w, h) if use_karaoke else _build_srt(subtitles)

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

    if sub_file and use_karaoke:
        # .ass carries its own embedded style block (incl. karaoke colours)
        filter_parts.append(f"[scaled]subtitles='{_escape_filter_path(sub_file)}'[out]")
    elif sub_file:
        filter_parts.append(
            f"[scaled]subtitles='{_escape_filter_path(sub_file)}':"
            f"force_style='FontSize=14,PrimaryColour=&H00FFFFFF,"
            f"OutlineColour=&H00000000,Outline=2,Alignment=2,"
            f"MarginV=40'[out]"
        )
    else:
        filter_parts.append("[scaled]copy[out]")

    has_bgm = bool(bgm_path and bgm_path.exists())
    if has_bgm:
        cmd.extend(["-i", str(bgm_path)])
    audio_filter = _build_audio_filter(has_bgm, duck=duck, duck_ratio=duck_ratio, bgm_volume=bgm_volume)

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
        # full stderr to disk -- the interesting line is rarely in the last 500 chars
        err_log = output_path.with_suffix(".ffmpeg-error.log")
        err_log.write_text("CMD: " + " ".join(cmd) + "\n\n" + result.stderr, encoding="utf-8")
        logger.error(f"FFmpeg failed (full stderr: {err_log}): {result.stderr[-500:]}")
        raise RuntimeError(f"FFmpeg compose failed, see {err_log.name}: {result.stderr[-300:]}")

    _cleanup_temp(concat_file, sub_file)
    logger.info(f"Video composed: {output_path} ({output_path.stat().st_size / 1024 / 1024:.1f} MB)")
    return output_path


def _build_concat_file(paths: list[Path], clip_duration: float, clip_durations: list[float] | None = None) -> Path:
    tmp = Path(tempfile.mktemp(suffix=".txt"))
    with open(tmp, "w", encoding="utf-8") as f:
        for i, p in enumerate(paths):
            dur = clip_durations[i] if clip_durations and i < len(clip_durations) else clip_duration
            # FFmpeg resolves concat entries relative to the list file; use absolute paths.
            abs_path = str(p.resolve()).replace("\\", "/").replace("'", "'\\''")
            f.write(f"file '{abs_path}'\n")
            f.write("inpoint 0\n")
            f.write(f"outpoint {dur:.3f}\n")
    return tmp


def _build_audio_filter(has_bgm: bool, duck: bool = True, duck_ratio: float = 8.0, bgm_volume: float = 0.3) -> str:
    """Audio graph: narration passthrough, or narration + bgm with optional
    sidechain ducking (bgm compressed by the voice signal, SPEC R2).

    Input indices: 1 = narration, 2 = bgm (subtitles are a filter source,
    not an -i input).
    """
    if not has_bgm:
        return "[1:a]aresample=44100[aout]"
    if not duck:
        return (
            f"[1:a]aresample=44100[voice];"
            f"[2:a]aresample=44100,volume={bgm_volume}[bgm];"
            f"[voice][bgm]amix=inputs=2:duration=first:dropout_transition=0[aout]"
        )
    return (
        f"[1:a]aresample=44100,asplit=2[voice][sc];"
        f"[2:a]aresample=44100,volume={bgm_volume}[bgmpre];"
        f"[bgmpre][sc]sidechaincompress=threshold=0.05:ratio={duck_ratio}:attack=20:release=400[bgmduck];"
        f"[voice][bgmduck]amix=inputs=2:duration=first:dropout_transition=0[aout]"
    )


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


# --- Karaoke ASS (SPEC R1) -------------------------------------------------

_ASS_FORMAT_LINE = (
    "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, "
    "Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, "
    "Shadow, Alignment, MarginL, MarginR, MarginV, Encoding"
)
_ASS_STYLE_LINE = (
    "Style: Karaoke,Arial,{fontsize},&H00FFFFFF,&H00A8A8A8,&H00000000,&H7F000000,"
    "-1,0,0,0,100,100,0,0,1,2,1,2,40,40,{margin_v},1"
)

_ASS_HEADER = (
    "[Script Info]\n"
    "ScriptType: v4.00+\n"
    "PlayResX: {w}\n"
    "PlayResY: {h}\n"
    "WrapStyle: 0\n"
    "ScaledBorderAndShadow: yes\n"
    "\n"
    "[V4+ Styles]\n" + _ASS_FORMAT_LINE + "\n" + _ASS_STYLE_LINE + "\n"
    "\n"
    "[Events]\n"
    "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
)

_KARAOKE_MAX_CHARS = 32
_KARAOKE_MAX_WORDS = 6


def _build_ass_karaoke(words: list[SubtitleEntry] | None, width: int, height: int) -> Path | None:
    """Build an .ass file with per-word \\k karaoke highlighting.

    Words are grouped into short lines (<=_KARAOKE_MAX_WORDS words or
    _KARAOKE_MAX_CHARS chars, hard break on sentence end). Each word gets
    a {\\kNN} tag where NN is its duration in centiseconds; inter-word
    gaps are absorbed into the preceding word so the highlight never
    drifts from the audio.
    """
    if not words:
        return None

    fontsize = max(14, int(height * 0.045))
    margin_v = int(height * 0.06)

    lines: list[list[SubtitleEntry]] = []
    current: list[SubtitleEntry] = []
    char_count = 0
    for w in words:
        if current and (len(current) >= _KARAOKE_MAX_WORDS or char_count + len(w.text) + 1 > _KARAOKE_MAX_CHARS):
            lines.append(current)
            current, char_count = [], 0
        current.append(w)
        char_count += len(w.text) + 1
        if w.text.rstrip().endswith((".", "!", "?", "\u3002", "\uff01", "\uff1f")):
            lines.append(current)
            current, char_count = [], 0
    if current:
        lines.append(current)

    tmp = Path(tempfile.mktemp(suffix=".ass"))
    with open(tmp, "w", encoding="utf-8-sig") as f:
        f.write(_ASS_HEADER.format(w=width, h=height, fontsize=fontsize, margin_v=margin_v))
        for line in lines:
            start, end = line[0].start, line[-1].end
            parts = []
            for idx, w in enumerate(line):
                # absorb the gap to the next word into this word's k-duration
                word_end = line[idx + 1].start if idx + 1 < len(line) else w.end
                k_cs = max(1, round((word_end - w.start) * 100))
                parts.append(f"{{\\k{k_cs}}}{_ass_escape(w.text)}")
            f.write(
                f"Dialogue: 0,{_format_ass_time(start)},{_format_ass_time(end)},Karaoke,,0,0,0,,{' '.join(parts)}\n"
            )
    return tmp


def _format_ass_time(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    cs = int(round((seconds % 1) * 100)) % 100
    return f"{h:d}:{m:02d}:{s:02d}.{cs:02d}"


def _ass_escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("{", "\\{").replace("}", "\\}").replace("\n", " ")
