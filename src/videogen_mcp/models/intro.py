from __future__ import annotations

from pydantic import BaseModel, Field


class IntroPack(BaseModel):
    id: str
    label: str = ""
    tone: str = ""  # serious | hilarious_contrast | deadpan | epic
    description: str = ""
    duration_hint: float = 8.0
    visual: dict = Field(default_factory=dict)
    audio: dict = Field(default_factory=dict)
    narration: dict = Field(default_factory=dict)
    structure: list[str] = Field(default_factory=list)
    post_intro: str = ""
    example_lines: list[str] = Field(default_factory=list)
