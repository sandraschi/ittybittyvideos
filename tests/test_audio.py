"""Tests for R2 (beat snap, ducking filter) and R9 (talker, overlay)."""

from __future__ import annotations

from pathlib import Path

import pytest

from videogen_mcp.services.audio import detect_beats, snap_cut_durations
from videogen_mcp.services.compose import _build_audio_filter, _build_concat_file
from videogen_mcp.services.overlay import _overlay_filter

# --- R2: snap_cut_durations ---------------------------------------------------


def test_snap_no_beats_returns_fixed_grid():
    assert snap_cut_durations(3, 5.0, None) == [5.0, 5.0, 5.0]
    assert snap_cut_durations(3, 5.0, []) == [5.0, 5.0, 5.0]


def test_snap_single_clip_untouched():
    assert snap_cut_durations(1, 5.0, [1.0, 2.0]) == [5.0]


def test_snap_cut_lands_on_beat_within_tolerance():
    # cut at 5.0, beat at 5.25 -> snapped; total of first clip = 5.25
    durations = snap_cut_durations(2, 5.0, beats=[1.0, 5.25, 9.0], tolerance=0.4)
    assert durations[0] == pytest.approx(5.25)


def test_snap_ignores_beat_outside_tolerance():
    durations = snap_cut_durations(2, 5.0, beats=[1.0, 6.2], tolerance=0.4)
    assert durations[0] == pytest.approx(5.0)


def test_snap_cuts_stay_monotonic_with_min_clip():
    # adversarial beat grid trying to pull two cuts onto the same beat
    durations = snap_cut_durations(3, 2.0, beats=[2.05, 2.1, 3.95], tolerance=0.4, min_clip=1.0)
    assert all(d >= 1.0 - 1e-9 for d in durations[:-1])
    cuts = []
    acc = 0.0
    for d in durations[:-1]:
        acc += d
        cuts.append(acc)
    assert cuts == sorted(cuts)


def test_snap_acceptance_cuts_on_detected_beats():
    # SPEC R2 acceptance: cut timestamps land on beats when within tolerance
    beats = [0.5 * i for i in range(40)]  # 120 BPM grid
    n = 4
    clip = 5.1
    durations = snap_cut_durations(n, clip, beats, tolerance=0.4)
    acc = 0.0
    for d in durations[:-1]:
        acc += d
        assert min(abs(acc - b) for b in beats) < 1e-6


def test_detect_beats_missing_file_returns_none(tmp_path):
    assert detect_beats(tmp_path / "nope.mp3") is None


# --- R2: ducking filter ---------------------------------------------------------


def test_audio_filter_no_bgm():
    f = _build_audio_filter(has_bgm=False)
    assert f == "[1:a]aresample=44100[aout]"


def test_audio_filter_bgm_no_duck():
    f = _build_audio_filter(has_bgm=True, duck=False, bgm_volume=0.25)
    assert "sidechaincompress" not in f
    assert "volume=0.25" in f
    assert "amix=inputs=2" in f


def test_audio_filter_bgm_duck():
    f = _build_audio_filter(has_bgm=True, duck=True, duck_ratio=12.0, bgm_volume=0.3)
    assert "asplit=2[voice][sc]" in f
    assert "sidechaincompress=threshold=0.05:ratio=12.0" in f
    assert f.endswith("[aout]")


def test_concat_file_per_clip_durations(tmp_path):
    clips = [tmp_path / "a.mp4", tmp_path / "b.mp4"]
    f = _build_concat_file(clips, clip_duration=5.0, clip_durations=[4.25, 5.75])
    content = Path(f).read_text()
    f.unlink()
    assert "outpoint 4.250" in content
    assert "outpoint 5.750" in content


# --- R9: overlay filter -----------------------------------------------------------


def test_overlay_filter_bottom_right():
    f = _overlay_filter("bottom-right", 0.28)
    assert "scale2ref=w=oh*mdar:h=ih*0.28" in f
    assert "overlay=x=main_w-w-main_h*0.03:y=main_h-h-main_h*0.03" in f


def test_overlay_filter_top_left():
    f = _overlay_filter("top-left", 0.2)
    assert "overlay=x=main_h*0.03:y=main_h*0.03" in f


def test_overlay_filter_rejects_bad_corner():
    with pytest.raises(ValueError, match="Unknown corner"):
        _overlay_filter("center", 0.28)


def test_overlay_filter_rejects_silly_scale():
    with pytest.raises(ValueError, match="sane range"):
        _overlay_filter("bottom-right", 0.9)


# --- R9: talker registry + provider ------------------------------------------------


def test_talker_registered():
    from videogen_mcp.providers import list_providers

    providers = list_providers()
    assert "talker" in providers
    assert "sadtalker" in providers["talker"]


def test_get_talker_empty_config_raises(monkeypatch):
    from videogen_mcp import config
    from videogen_mcp.providers import get_talker

    config.get_settings.cache_clear()
    monkeypatch.delenv("VIDEOGEN_TALKER_PROVIDER", raising=False)
    with pytest.raises(ValueError, match="No talker provider configured"):
        get_talker()
    config.get_settings.cache_clear()


@pytest.mark.asyncio
async def test_talker_missing_image_raises(tmp_path):
    from videogen_mcp.providers.talker_sadtalker import SadTalkerProvider

    p = SadTalkerProvider()
    audio = tmp_path / "a.mp3"
    audio.write_bytes(b"\x00")
    with pytest.raises(FileNotFoundError, match="source image"):
        await p.synthesize_head(audio, tmp_path / "benny.jpg", tmp_path / "out.mp4")
