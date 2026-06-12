from __future__ import annotations

from pydantic import BaseModel, Field


class TropeBeat(BaseModel):
    scene_type: str
    narration_goal: str
    duration_hint: float = 10.0


class TropeTemplate(BaseModel):
    id: str
    label: str = ""
    video_types: list[str] = Field(default_factory=list)
    beats: list[TropeBeat] = Field(default_factory=list)
    example_hook: str = ""
    exemplar_views: str = ""
    exemplar_refs: list[str] = Field(default_factory=list)
    visual: dict = Field(default_factory=dict)
    expand_to_mid: dict = Field(default_factory=dict)
    credits: dict = Field(default_factory=dict)
    intro: dict = Field(default_factory=dict)
