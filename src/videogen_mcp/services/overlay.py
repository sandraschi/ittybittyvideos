"""Picture-in-picture overlay for talking heads (SPEC R9).

Pure FFmpeg compositing: the head video is scaled relative to the main
video's height and pinned to a corner with a margin. The head's own
audio (if any) is dropped -- narration already lives in the main video.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from loguru import logger

_MARGIN_FRAC = 0.03

_CORNERS = {
    "bottom-right": ("W-w-{m}", "H-h-{m}"),
    "bottom-left": ("{m}", "H-h-{m}"),
    "top-right": ("W-w-{m}", "{m}"),
    "top-left": ("{m}", "{m}"),
}


def _overlay_filter(corner: str, scale: float) -> str:
    """Build the filter_complex string. Extracted for unit testing.

    scale2ref sizes the head relative to the MAIN video's height (ih = ref
    input height; oh*mdar preserves the head's own aspect ratio)."""
    if corner not in _CORNERS:
        raise ValueError(f"Unknown corner '{corner}'. Use one of: {list(_CORNERS)}")
    if not 0.05 <= scale <= 0.6:
        raise ValueError(f"Talker scale {scale} outside sane range 0.05-0.6")
    x_t, y_t = _CORNERS[corner]
    margin = f"main_h*{_MARGIN_FRAC:.2f}"
    x = x_t.format(m=margin).replace("W", "main_w").replace("H", "main_h")
    y = y_t.format(m=margin).replace("W", "main_w").replace("H", "main_h")
    return (
        f"[1:v][0:v]scale2ref=w=oh*mdar:h=ih*{scale}[head][base];"
        f"[base][head]overlay=x={x}:y={y}:shortest=0[out]"
    )


def overlay_talking_head(
    main_video: Path,
    head_video: Path,
    output_path: Path,
    corner: str = "bottom-right",
    scale: float = 0.28,
) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(main_video),
        "-i",
        str(head_video),
        "-filter_complex",
        _overlay_filter(corner, scale),
        "-map",
        "[out]",
        "-map",
        "0:a",
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "23",
        "-c:a",
        "copy",
        "-movflags",
        "+faststart",
        str(output_path),
    ]
    logger.info(f"Overlay: {head_video.name} onto {main_video.name} ({corner}, {scale:.0%})")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if result.returncode != 0:
        logger.error(f"Overlay failed: {result.stderr[-400:]}")
        raise RuntimeError(f"FFmpeg overlay failed: {result.stderr[-200:]}")
    return output_path
