from __future__ import annotations

from pydantic import BaseModel, Field


class CreditEntry(BaseModel):
    name: str
    role: str


class CreditsPack(BaseModel):
    id: str
    label: str = ""
    description: str = ""
    min_contributors: int = 40
    max_contributors: int = 200
    featured: list[CreditEntry] = Field(default_factory=list)
    departments: list[str] = Field(default_factory=list)
    pool: list[CreditEntry] = Field(default_factory=list)
    filler_templates: list[str] = Field(default_factory=list)
    post_credits_stingers: list[str] = Field(default_factory=list)
