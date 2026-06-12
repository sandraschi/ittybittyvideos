"""Critique models for the Screening Room (SPEC R3)."""

from __future__ import annotations

import enum

from pydantic import BaseModel, Field


class SceneIssue(str, enum.Enum):
    FOOTAGE_MISMATCH = "footage_mismatch"
    PACING = "pacing"
    SUB_COLLISION = "sub_collision"
    WEAK_HOOK = "weak_hook"


class SceneCritique(BaseModel):
    scene_index: int
    verdict: str = Field(description="'pass' or 'flag'")
    issues: list[SceneIssue] = []
    fix_hint: str = Field(default="", description="Editor note; for footage_mismatch, usable as a search query.")


class CritiqueReport(BaseModel):
    pass_number: int
    model: str
    scenes: list[SceneCritique]

    @property
    def flagged(self) -> list[SceneCritique]:
        return [c for c in self.scenes if c.verdict == "flag"]

    @property
    def footage_flags(self) -> list[SceneCritique]:
        return [c for c in self.flagged if SceneIssue.FOOTAGE_MISMATCH in c.issues]
