from __future__ import annotations

import enum
from typing import Annotated

from pydantic import BaseModel, Field

from videogen_mcp.models.visual_look import VisualLook


class VideoType(str, enum.Enum):
    TUTORIAL = "tutorial"
    DEMO = "demo"
    EXPLAINER = "explainer"
    DOCUMENTARY = "documentary"
    SHOWCASE = "showcase"


class SceneType(str, enum.Enum):
    HOOK = "hook"
    INTRO = "intro"
    EXPLAINER = "explainer"
    DEMO = "demo"
    BROLL = "broll"
    RECAP = "recap"
    OUTRO = "outro"
    TRANSITION = "transition"


class ShotType(str, enum.Enum):
    WIDE = "wide"
    MEDIUM = "medium"
    CLOSE = "close"
    SCREEN_CAPTURE = "screen_capture"
    TEXT_OVERLAY = "text_overlay"
    AERIAL = "aerial"


class TransitionType(str, enum.Enum):
    CUT = "cut"
    CROSSFADE = "crossfade"
    FADE_BLACK = "fade_black"
    WIPE = "wipe"


class Scene(BaseModel):
    scene_type: SceneType
    title: Annotated[str, Field(description="Short scene label for the editor.")]
    narration: Annotated[str, Field(description="Spoken narration for this scene.")]
    search_terms: Annotated[list[str], Field(description="Stock footage / AI video search terms.")]
    shot_type: ShotType = ShotType.MEDIUM
    duration_target: Annotated[float, Field(description="Target seconds for this scene.", ge=2.0, le=120.0)] = 10.0
    transition_out: TransitionType = TransitionType.CUT
    notes: str = ""


class Chapter(BaseModel):
    title: Annotated[str, Field(description="Chapter heading (for markers/TOC).")]
    scenes: list[Scene]

    @property
    def duration(self) -> float:
        return sum(s.duration_target for s in self.scenes)


class Storyboard(BaseModel):
    title: Annotated[str, Field(description="Video title.")]
    video_type: VideoType
    target_duration: Annotated[float, Field(description="Total target duration in seconds.")]
    chapters: list[Chapter]
    language: str = "en"

    @property
    def total_scenes(self) -> int:
        return sum(len(ch.scenes) for ch in self.chapters)

    @property
    def planned_duration(self) -> float:
        return sum(ch.duration for ch in self.chapters)

    @property
    def all_scenes(self) -> list[Scene]:
        return [s for ch in self.chapters for s in ch.scenes]


class PlanRequest(BaseModel):
    topic: Annotated[str, Field(description="Video topic or subject.")]
    video_type: VideoType = VideoType.EXPLAINER
    target_duration: Annotated[float, Field(description="Target length in seconds.", ge=30, le=900)] = 300.0
    language: str = "en"
    chapters: Annotated[int, Field(description="Number of chapters/sections.", ge=1, le=12)] = 4
    style_notes: str = ""
    visual_style: str = ""
    visual_material: str = ""
    visual_tone: str = ""

    def visual_look(self) -> VisualLook:
        return VisualLook(
            visual_style=self.visual_style,
            visual_material=self.visual_material,
            visual_tone=self.visual_tone,
        )
