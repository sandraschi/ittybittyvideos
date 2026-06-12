"""Forced alignment service -- universal word-level subtitle timing (SPEC R1).

Runs faster-whisper on *generated* TTS audio to recover word timestamps,
regardless of which TTS provider produced it. This replaces per-provider
timestamp plumbing (CosyVoice's duration heuristic, future providers)
with one post-pass.

Design notes:
- We know the ground-truth text (we wrote the script), so whisper's
  transcription is only used for *timing*. Whisper words are mapped back
  onto the canonical script tokens via difflib sequence matching, so the
  burned subtitles always show the script's spelling and punctuation,
  never whisper's transcription errors.
- faster-whisper is an optional dependency (`uv sync --extra align`).
  When it is missing or model load fails, align_words() returns None and
  logs why -- callers fall back to provider-native subtitles. No fake
  success (IMPLEMENTATION_HONESTY_STANDARD).
- Model is loaded lazily once per process (it is several hundred MB).
"""

from __future__ import annotations

import difflib
import re
from functools import lru_cache
from pathlib import Path

from loguru import logger

from videogen_mcp.config import get_settings
from videogen_mcp.providers.base import SubtitleEntry

_SENTENCE_END = (".", "!", "?", "\u3002", "\uff01", "\uff1f")


def is_available() -> bool:
    """True if faster-whisper is importable. Does not load the model."""
    try:
        import faster_whisper  # type: ignore[import-not-found]  # noqa: F401

        return True
    except ImportError:
        return False


@lru_cache(maxsize=1)
def _get_model():
    """Lazily load the whisper model once. Raises on failure (caught by align_words)."""
    from faster_whisper import WhisperModel  # type: ignore[import-not-found]

    settings = get_settings()
    model_name = settings.videogen_whisper_model
    device = settings.videogen_whisper_device
    compute = "float16" if device == "cuda" else "auto"
    logger.info(f"Loading faster-whisper model '{model_name}' (device={device})")
    return WhisperModel(model_name, device=device, compute_type=compute)


def align_words(audio_path: Path, text: str, language: str | None = None) -> list[SubtitleEntry] | None:
    """Recover word-level timestamps for `text` from its rendered audio.

    Returns word-level SubtitleEntry list with canonical script tokens,
    or None when alignment is unavailable or failed (caller must fall
    back to provider subtitles).
    """
    if not is_available():
        logger.warning("align: faster-whisper not installed (uv sync --extra align); falling back to provider subs")
        return None
    if not audio_path.exists():
        logger.warning(f"align: audio file missing: {audio_path}")
        return None

    try:
        model = _get_model()
        segments, _info = model.transcribe(
            str(audio_path),
            language=language,
            word_timestamps=True,
            vad_filter=True,
            beam_size=5,
        )
        whisper_words: list[SubtitleEntry] = []
        for seg in segments:
            for w in seg.words or []:
                token = w.word.strip()
                if token:
                    whisper_words.append(SubtitleEntry(start=float(w.start), end=float(w.end), text=token))
    except Exception as e:
        logger.warning(f"align: transcription failed ({e}); falling back to provider subs")
        return None

    if not whisper_words:
        logger.warning("align: whisper produced no words; falling back to provider subs")
        return None

    aligned = _map_to_canonical(whisper_words, text)
    logger.debug(f"align: {len(whisper_words)} whisper words -> {len(aligned)} canonical words")
    return aligned


def _normalize(token: str) -> str:
    return re.sub(r"[^\w]", "", token, flags=re.UNICODE).lower()


def _map_to_canonical(whisper_words: list[SubtitleEntry], text: str) -> list[SubtitleEntry]:
    """Map whisper timing onto the canonical script tokens.

    Uses difflib on normalized tokens. Canonical tokens without a whisper
    match (rare: disfluencies, numbers read differently) are interpolated
    between their timed neighbours so every script word gets a slot.
    """
    canonical = text.split()
    if not canonical:
        return whisper_words

    norm_canon = [_normalize(t) for t in canonical]
    norm_whisper = [_normalize(w.text) for w in whisper_words]

    matcher = difflib.SequenceMatcher(a=norm_canon, b=norm_whisper, autojunk=False)
    timed: list[SubtitleEntry | None] = [None] * len(canonical)

    for block in matcher.get_matching_blocks():
        for k in range(block.size):
            w = whisper_words[block.b + k]
            timed[block.a + k] = SubtitleEntry(start=w.start, end=w.end, text=canonical[block.a + k])

    return _interpolate_gaps(timed, canonical, whisper_words)


def _interpolate_gaps(
    timed: list[SubtitleEntry | None],
    canonical: list[str],
    whisper_words: list[SubtitleEntry],
) -> list[SubtitleEntry]:
    """Fill unmatched canonical tokens by spreading them across the gap
    between the nearest timed neighbours."""
    result: list[SubtitleEntry] = []
    i = 0
    n = len(timed)
    audio_start = whisper_words[0].start
    audio_end = whisper_words[-1].end

    while i < n:
        if timed[i] is not None:
            result.append(timed[i])  # type: ignore[arg-type]
            i += 1
            continue
        # gap [i, j)
        j = i
        while j < n and timed[j] is None:
            j += 1
        gap_start = result[-1].end if result else audio_start
        gap_end = timed[j].start if j < n else audio_end  # type: ignore[union-attr]
        if gap_end <= gap_start:
            gap_end = gap_start + 0.05 * (j - i)
        step = (gap_end - gap_start) / (j - i)
        for k in range(i, j):
            s = gap_start + (k - i) * step
            result.append(SubtitleEntry(start=s, end=s + step, text=canonical[k]))
        i = j

    return result


def words_to_sentences(words: list[SubtitleEntry], max_chars: int = 84) -> list[SubtitleEntry]:
    """Regroup word entries into sentence-level subtitles.

    Breaks on sentence-ending punctuation or when a line would exceed
    max_chars. Timing comes from the first/last word of each group, so
    sentence subs derived from aligned words inherit real audio timing
    (the CosyVoice fix).
    """
    if not words:
        return []

    sentences: list[SubtitleEntry] = []
    group: list[SubtitleEntry] = []
    length = 0

    for w in words:
        if group and length + len(w.text) + 1 > max_chars:
            sentences.append(_flush(group))
            group, length = [], 0
        group.append(w)
        length += len(w.text) + 1
        if w.text.rstrip().endswith(_SENTENCE_END):
            sentences.append(_flush(group))
            group, length = [], 0

    if group:
        sentences.append(_flush(group))
    return sentences


def _flush(group: list[SubtitleEntry]) -> SubtitleEntry:
    return SubtitleEntry(start=group[0].start, end=group[-1].end, text=" ".join(w.text for w in group))
