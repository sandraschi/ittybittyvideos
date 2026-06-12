"""Tests for the R1 alignment service and karaoke subtitle generation.

faster-whisper is never required: availability tests monkeypatch the import
machinery, and timing-mapping tests inject a fake module into sys.modules.
"""

from __future__ import annotations

import sys
import types
from pathlib import Path

import pytest

from videogen_mcp.providers.base import SubtitleEntry
from videogen_mcp.services import align
from videogen_mcp.services.align import _map_to_canonical, align_words, words_to_sentences
from videogen_mcp.services.compose import _build_ass_karaoke, _format_ass_time


def _w(start: float, end: float, text: str) -> SubtitleEntry:
    return SubtitleEntry(start=start, end=end, text=text)


# --- words_to_sentences ------------------------------------------------------


def test_words_to_sentences_breaks_on_punctuation():
    words = [_w(0.0, 0.3, "Hello"), _w(0.3, 0.6, "world."), _w(0.7, 1.0, "Bye.")]
    sents = words_to_sentences(words)
    assert len(sents) == 2
    assert sents[0].text == "Hello world."
    assert sents[0].start == 0.0
    assert sents[0].end == 0.6
    assert sents[1].text == "Bye."


def test_words_to_sentences_breaks_on_max_chars():
    words = [_w(i * 0.5, i * 0.5 + 0.4, "wordy") for i in range(40)]
    sents = words_to_sentences(words, max_chars=30)
    assert len(sents) > 1
    assert all(len(s.text) <= 30 + len("wordy") for s in sents)


def test_words_to_sentences_cjk_punctuation():
    words = [_w(0.0, 0.4, "\u4f60\u597d\u3002"), _w(0.5, 0.9, "\u518d\u89c1\u3002")]
    sents = words_to_sentences(words)
    assert len(sents) == 2


def test_words_to_sentences_empty():
    assert words_to_sentences([]) == []


# --- canonical mapping -------------------------------------------------------


def test_map_to_canonical_exact_match():
    whisper = [_w(0.0, 0.3, "hello"), _w(0.3, 0.7, "brave"), _w(0.7, 1.1, "world")]
    out = _map_to_canonical(whisper, "Hello, brave world!")
    assert [e.text for e in out] == ["Hello,", "brave", "world!"]
    assert out[0].start == 0.0
    assert out[2].end == 1.1


def test_map_to_canonical_interpolates_missing_word():
    # whisper dropped "very"; it must be interpolated between neighbours
    whisper = [_w(0.0, 0.3, "a"), _w(1.0, 1.4, "good"), _w(1.4, 1.8, "day")]
    out = _map_to_canonical(whisper, "a very good day")
    assert [e.text for e in out] == ["a", "very", "good", "day"]
    very = out[1]
    assert 0.3 <= very.start < 1.0
    assert very.end <= 1.0 + 1e-6


def test_map_to_canonical_timing_within_tolerance():
    # SPEC R1 acceptance: timing within 150ms of source timestamps
    whisper = [_w(0.000, 0.310, "quantum"), _w(0.310, 0.940, "computing"), _w(0.940, 1.500, "explained")]
    out = _map_to_canonical(whisper, "Quantum computing explained.")
    for src, mapped in zip(whisper, out):
        assert abs(src.start - mapped.start) <= 0.150
        assert abs(src.end - mapped.end) <= 0.150


# --- align_words availability / degradation ----------------------------------


def test_align_words_unavailable_returns_none(monkeypatch, tmp_path):
    monkeypatch.setattr(align, "is_available", lambda: False)
    audio = tmp_path / "a.mp3"
    audio.write_bytes(b"\x00")
    assert align_words(audio, "some text") is None


def test_align_words_missing_audio_returns_none(monkeypatch, tmp_path):
    monkeypatch.setattr(align, "is_available", lambda: True)
    assert align_words(tmp_path / "does_not_exist.mp3", "text") is None


def test_align_words_with_fake_whisper(monkeypatch, tmp_path):
    class FakeWord:
        def __init__(self, start, end, word):
            self.start, self.end, self.word = start, end, word

    class FakeSegment:
        def __init__(self, words):
            self.words = words

    class FakeModel:
        def __init__(self, *a, **k):
            pass

        def transcribe(self, *a, **k):
            segs = [FakeSegment([FakeWord(0.0, 0.4, " Hello"), FakeWord(0.4, 0.9, " world")])]
            return iter(segs), {}

    fake = types.ModuleType("faster_whisper")
    fake.WhisperModel = FakeModel
    monkeypatch.setitem(sys.modules, "faster_whisper", fake)
    align._get_model.cache_clear()

    audio = tmp_path / "a.mp3"
    audio.write_bytes(b"\x00")
    out = align_words(audio, "Hello world.")
    align._get_model.cache_clear()

    assert out is not None
    assert [e.text for e in out] == ["Hello", "world."]
    assert out[0].start == pytest.approx(0.0)
    assert out[1].end == pytest.approx(0.9)


# --- karaoke ASS -------------------------------------------------------------


def test_ass_time_format():
    assert _format_ass_time(0.0) == "0:00:00.00"
    assert _format_ass_time(61.5) == "0:01:01.50"
    assert _format_ass_time(3661.25) == "1:01:01.25"


def test_build_ass_karaoke_none_on_empty():
    assert _build_ass_karaoke(None, 1280, 720) is None
    assert _build_ass_karaoke([], 1280, 720) is None


def test_build_ass_karaoke_k_tags_centiseconds(tmp_path):
    words = [_w(0.0, 0.5, "Fifty"), _w(0.5, 1.5, "hundred.")]
    path = _build_ass_karaoke(words, 1280, 720)
    assert path is not None
    content = Path(path).read_text(encoding="utf-8-sig")
    path.unlink()

    assert "[V4+ Styles]" in content
    assert "PlayResX: 1280" in content
    # 0.5s -> {\k50}, 1.0s -> {\k100}
    assert "{\\k50}Fifty" in content
    assert "{\\k100}hundred." in content
    assert "Dialogue: 0,0:00:00.00,0:00:01.50,Karaoke" in content


def test_build_ass_karaoke_absorbs_inter_word_gap(tmp_path):
    # gap 0.5->0.8 between words must be absorbed into the first word's \k
    words = [_w(0.0, 0.5, "wait"), _w(0.8, 1.2, "for"), _w(1.2, 1.6, "it.")]
    path = _build_ass_karaoke(words, 1280, 720)
    content = Path(path).read_text(encoding="utf-8-sig")
    path.unlink()
    # first word k = (0.8 - 0.0) * 100 = 80, not 50
    assert "{\\k80}wait" in content


def test_build_ass_karaoke_line_break_on_sentence_end(tmp_path):
    words = [_w(0.0, 0.4, "One."), _w(0.5, 0.9, "Two.")]
    path = _build_ass_karaoke(words, 1280, 720)
    content = Path(path).read_text(encoding="utf-8-sig")
    path.unlink()
    assert content.count("Dialogue:") == 2


def test_build_ass_karaoke_escapes_braces(tmp_path):
    words = [_w(0.0, 0.4, "{weird}")]
    path = _build_ass_karaoke(words, 1280, 720)
    content = Path(path).read_text(encoding="utf-8-sig")
    path.unlink()
    assert "\\{weird\\}" in content


# --- TTSResult.words plumbing -------------------------------------------------


def test_ttsresult_words_default_none():
    from videogen_mcp.providers.base import TTSResult

    r = TTSResult(audio_path=Path("x.mp3"), duration=1.0, subtitles=[])
    assert r.words is None
