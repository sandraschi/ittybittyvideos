"""Audio analysis service -- beat detection and cut snapping (SPEC R2).

Beat grid comes from librosa (optional: `uv sync --extra beats`). When
librosa is missing or analysis fails, detect_beats() returns None and
callers keep the un-snapped cut grid. No fake success.
"""

from __future__ import annotations

from pathlib import Path

from loguru import logger

_MIN_CLIP_SECONDS = 1.0


def beats_available() -> bool:
    try:
        import librosa  # type: ignore[import-not-found]  # noqa: F401

        return True
    except ImportError:
        return False


def detect_beats(audio_path: Path) -> list[float] | None:
    """Return beat timestamps (seconds) for an audio file, or None.

    None means "no beat grid" (librosa missing, unreadable file, or no
    beats found) -- callers must fall back to the regular cut grid.
    """
    if not beats_available():
        logger.warning("beats: librosa not installed (uv sync --extra beats); cuts stay on the fixed grid")
        return None
    if not audio_path.exists():
        logger.warning(f"beats: audio file missing: {audio_path}")
        return None

    try:
        import librosa  # type: ignore[import-not-found]

        y, sr = librosa.load(str(audio_path), mono=True)
        tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr, units="frames")
        beat_times = librosa.frames_to_time(beat_frames, sr=sr)
        beats = [float(t) for t in beat_times]
        logger.debug(f"beats: {len(beats)} beats @ ~{float(tempo):.0f} BPM in {audio_path.name}")
        return beats or None
    except Exception as e:
        logger.warning(f"beats: analysis failed ({e}); cuts stay on the fixed grid")
        return None


def snap_cut_durations(
    n_clips: int,
    clip_duration: float,
    beats: list[float] | None,
    tolerance: float = 0.4,
    min_clip: float = _MIN_CLIP_SECONDS,
) -> list[float]:
    """Snap the fixed cut grid to the nearest beats and return per-clip durations.

    Cut points live at clip_duration * i (i = 1..n-1). Each is moved to the
    nearest beat within +-tolerance seconds; points with no beat in range
    stay put. Snapped points are kept strictly increasing and every clip
    keeps at least min_clip seconds, so pacing can never collapse.
    """
    base = [clip_duration * i for i in range(1, n_clips)]
    if not beats or n_clips <= 1:
        return [clip_duration] * n_clips

    snapped: list[float] = []
    prev = 0.0
    for cut in base:
        candidate = _nearest(beats, cut)
        if candidate is not None and abs(candidate - cut) <= tolerance:
            cut = candidate
        cut = max(cut, prev + min_clip)  # monotonic + pacing floor
        snapped.append(cut)
        prev = cut

    durations = []
    prev = 0.0
    for cut in snapped:
        durations.append(cut - prev)
        prev = cut
    durations.append(clip_duration)  # last clip keeps nominal length
    return durations


def _nearest(beats: list[float], t: float) -> float | None:
    if not beats:
        return None
    return min(beats, key=lambda b: abs(b - t))
