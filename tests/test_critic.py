"""Tests for R3 Screening Room: JSON parsing, midpoints, refetch logic."""

from __future__ import annotations

from pathlib import Path

import pytest

from videogen_mcp.models.critique import CritiqueReport, SceneCritique, SceneIssue
from videogen_mcp.models.storyboard import Scene, SceneType
from videogen_mcp.services.critic import parse_critique_json, refetch_queries, scene_midpoints


def _scene(title: str = "s", narration: str = "n", terms: list[str] | None = None) -> Scene:
    return Scene(
        scene_type=SceneType.BROLL,
        title=title,
        narration=narration,
        search_terms=terms or ["ocean", "waves"],
    )


# --- midpoints ---------------------------------------------------------------


def test_scene_midpoints():
    assert scene_midpoints(3, 10.0) == [5.0, 15.0, 25.0]
    assert scene_midpoints(0, 10.0) == []


# --- JSON parsing ------------------------------------------------------------


def test_parse_clean_json():
    c = parse_critique_json('{"verdict": "flag", "issues": ["footage_mismatch"], "fix_hint": "city skyline"}', 2)
    assert c.scene_index == 2
    assert c.verdict == "flag"
    assert c.issues == [SceneIssue.FOOTAGE_MISMATCH]
    assert c.fix_hint == "city skyline"


def test_parse_fenced_json():
    raw = '```json\n{"verdict": "pass", "issues": [], "fix_hint": ""}\n```'
    c = parse_critique_json(raw, 0)
    assert c.verdict == "pass"


def test_parse_json_with_chatter():
    raw = 'Sure! Here is my review: {"verdict": "flag", "issues": ["pacing"], "fix_hint": "tighten"} Hope that helps!'
    c = parse_critique_json(raw, 1)
    assert c.verdict == "flag"
    assert c.issues == [SceneIssue.PACING]


def test_parse_garbage_defaults_to_pass():
    c = parse_critique_json("the footage is, like, fine I guess", 4)
    assert c.verdict == "pass"
    assert c.issues == []


def test_parse_unknown_issue_dropped():
    c = parse_critique_json('{"verdict": "flag", "issues": ["bad_vibes", "sub_collision"], "fix_hint": ""}', 0)
    assert c.issues == [SceneIssue.SUB_COLLISION]


def test_parse_invalid_verdict_normalized():
    c = parse_critique_json('{"verdict": "maybe", "issues": [], "fix_hint": ""}', 0)
    assert c.verdict == "pass"


# --- refetch queries ----------------------------------------------------------


def test_refetch_queries_uses_fix_hint():
    report = CritiqueReport(
        pass_number=1,
        model="m",
        scenes=[
            SceneCritique(scene_index=0, verdict="pass"),
            SceneCritique(
                scene_index=1, verdict="flag", issues=[SceneIssue.FOOTAGE_MISMATCH], fix_hint="alpine meadow"
            ),
        ],
    )
    q = refetch_queries(report, [_scene(), _scene()])
    assert q == {1: "alpine meadow"}


def test_refetch_queries_falls_back_to_search_terms():
    report = CritiqueReport(
        pass_number=1,
        model="m",
        scenes=[SceneCritique(scene_index=0, verdict="flag", issues=[SceneIssue.FOOTAGE_MISMATCH], fix_hint="  ")],
    )
    q = refetch_queries(report, [_scene(terms=["tokyo", "night", "rain"])])
    assert q == {0: "tokyo night rain"}


def test_refetch_ignores_non_footage_flags():
    report = CritiqueReport(
        pass_number=1,
        model="m",
        scenes=[SceneCritique(scene_index=0, verdict="flag", issues=[SceneIssue.PACING], fix_hint="x")],
    )
    assert refetch_queries(report, [_scene()]) == {}


def test_refetch_ignores_out_of_range_index():
    report = CritiqueReport(
        pass_number=1,
        model="m",
        scenes=[SceneCritique(scene_index=7, verdict="flag", issues=[SceneIssue.FOOTAGE_MISMATCH], fix_hint="x")],
    )
    assert refetch_queries(report, [_scene()]) == {}


# --- SPEC R3 acceptance: mismatched clip gets flagged and replaced -------------


@pytest.mark.asyncio
async def test_flagged_scene_footage_replaced(monkeypatch, tmp_path):
    """A footage_mismatch flag must lead to a different clip for that scene."""
    from videogen_mcp.providers.base import StockClip
    from videogen_mcp.services import pipeline_extended
    from videogen_mcp.services.pipeline_extended import _fetch_scene_footage

    old_clip = tmp_path / "old.mp4"
    new_clip = tmp_path / "new.mp4"
    old_clip.write_bytes(b"0")
    new_clip.write_bytes(b"0")

    class FakeStock:
        async def search(self, query: str, count: int = 3, aspect: str = "9:16"):
            return [
                StockClip(url="u-old", duration=5, width=1080, height=1920, source="old"),
                StockClip(url="u-new", duration=5, width=1080, height=1920, source="new"),
            ]

        async def download(self, clip, dest):
            return old_clip if clip.url == "u-old" else new_clip

    monkeypatch.setattr(pipeline_extended, "get_stock", lambda: FakeStock())
    monkeypatch.setattr(pipeline_extended, "is_cached", lambda url: None)
    monkeypatch.setattr(pipeline_extended, "cache_path", lambda url: tmp_path / "ignored.mp4")

    scene = _scene(terms=["mountain"])
    # critique said: this clip doesn't match, try "alpine meadow"; old clip excluded
    replacement = await _fetch_scene_footage(
        scene, aspect=_aspect(), dest=tmp_path / "f.mp4", query_override="alpine meadow", exclude={old_clip}
    )
    assert replacement == new_clip
    assert replacement != old_clip


def _aspect():
    from videogen_mcp.models.schema import VideoAspect

    return VideoAspect.PORTRAIT


# --- report properties ----------------------------------------------------------


def test_report_flag_properties():
    report = CritiqueReport(
        pass_number=1,
        model="m",
        scenes=[
            SceneCritique(scene_index=0, verdict="pass"),
            SceneCritique(scene_index=1, verdict="flag", issues=[SceneIssue.WEAK_HOOK]),
            SceneCritique(scene_index=2, verdict="flag", issues=[SceneIssue.FOOTAGE_MISMATCH]),
        ],
    )
    assert len(report.flagged) == 2
    assert len(report.footage_flags) == 1
    assert report.footage_flags[0].scene_index == 2


def test_critique_json_roundtrip(tmp_path: Path):
    report = CritiqueReport(
        pass_number=2,
        model="qwen3.5-vl",
        scenes=[SceneCritique(scene_index=0, verdict="flag", issues=[SceneIssue.SUB_COLLISION], fix_hint="raise subs")],
    )
    f = tmp_path / "critique.json"
    f.write_text(report.model_dump_json(indent=2), encoding="utf-8")
    loaded = CritiqueReport.model_validate_json(f.read_text(encoding="utf-8"))
    assert loaded.scenes[0].issues == [SceneIssue.SUB_COLLISION]
