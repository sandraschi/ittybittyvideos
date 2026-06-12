from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone
from typing import Annotated

from pydantic import BaseModel, Field

from videogen_mcp.models.visual_look import VisualLook


class VideoAspect(str, enum.Enum):
    PORTRAIT = "9:16"
    LANDSCAPE = "16:9"
    SQUARE = "1:1"

    @property
    def resolution(self) -> tuple[int, int]:
        return {
            "9:16": (1080, 1920),
            "16:9": (1920, 1080),
            "1:1": (1080, 1080),
        }[self.value]


class JobStatus(str, enum.Enum):
    PENDING = "pending"
    SCRIPTING = "scripting"
    FETCHING_FOOTAGE = "fetching_footage"
    GENERATING_VOICE = "generating_voice"
    COMPOSING = "composing"
    COMPLETE = "complete"
    FAILED = "failed"


class ScriptSegment(BaseModel):
    narration: Annotated[str, Field(description="Narration text for this segment.")]
    search_terms: Annotated[list[str], Field(description="Stock footage search keywords.")]


class VideoScript(BaseModel):
    title: Annotated[str, Field(description="Video title for metadata/social.")]
    segments: Annotated[list[ScriptSegment], Field(description="Ordered narration segments.")]


class GenerateRequest(BaseModel):
    topic: Annotated[str, Field(description="Topic or keyword for the video.")] = ""
    script: Annotated[str | None, Field(description="Custom script (skips LLM generation).")] = None
    aspect: Annotated[VideoAspect, Field(description="Video aspect ratio.")] = VideoAspect.PORTRAIT
    voice: Annotated[str, Field(description="TTS voice identifier.")] = ""
    clip_duration: Annotated[
        float, Field(description="Target duration per footage clip in seconds.", ge=2.0, le=30.0)
    ] = 5.0
    paragraph_count: Annotated[int, Field(description="Number of script segments.", ge=1, le=10)] = 3
    bgm_url: Annotated[str, Field(description="URL to background music file.")] = ""
    template: Annotated[str, Field(description="Video style template name.")] = "default"
    llm_provider: Annotated[
        str,
        Field(description="Topic scripting LLM: deepseek | openai | lmstudio | ollama (ignored when script is set)."),
    ] = ""
    visual_style: Annotated[str, Field(description="AI footage style preset (localgen/veo/omni).")] = ""
    visual_material: Annotated[str, Field(description="AI footage material preset.")] = ""
    visual_tone: Annotated[str, Field(description="AI footage tone preset.")] = ""
    structure: Annotated[
        str, Field(description="R10 narrative preset, e.g. trope:pet-food-duo-review.")
    ] = ""
    style_notes: Annotated[str, Field(description="Extra style guidance for LLM scripting.")] = ""

    def visual_look(self) -> VisualLook:
        return VisualLook(
            visual_style=self.visual_style,
            visual_material=self.visual_material,
            visual_tone=self.visual_tone,
        )


class JobInfo(BaseModel):
    job_id: str = Field(default_factory=lambda: uuid.uuid4().hex[:12])
    status: JobStatus = JobStatus.PENDING
    progress: float = 0.0
    topic: str = ""
    output_path: str = ""
    error: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def update(self, status: JobStatus, progress: float = 0.0) -> None:
        self.status = status
        self.progress = progress
        self.updated_at = datetime.now(timezone.utc)
