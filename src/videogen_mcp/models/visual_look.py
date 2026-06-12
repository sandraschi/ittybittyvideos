"""Visual look selectors for AI-generated footage prompts (LocalGen, Veo, Omni)."""

from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, Field

AI_STOCK_PROVIDERS = frozenset({"localgen", "cogvideo", "veo", "omni"})

LOOK_CATALOG: dict[str, list[dict[str, str]]] = {
    "styles": [
        {"id": "", "label": "Default"},
        {"id": "cinematic", "label": "Cinematic", "prompt": "cinematic lighting, shallow depth of field, film grain"},
        {"id": "documentary", "label": "Documentary", "prompt": "documentary realism, natural light, handheld feel"},
        {"id": "anime", "label": "Anime", "prompt": "anime illustration style, cel shading, vibrant colors"},
        {"id": "surreal", "label": "Surreal", "prompt": "surreal dreamlike atmosphere, impossible scale"},
        {"id": "minimalist", "label": "Minimalist", "prompt": "minimalist composition, clean negative space"},
    ],
    "materials": [
        {"id": "", "label": "Default"},
        {"id": "oil_paint", "label": "Oil paint", "prompt": "oil painting style, visible brushstrokes, canvas texture"},
        {"id": "watercolor", "label": "Watercolor", "prompt": "watercolor wash, soft edges, paper texture"},
        {"id": "origami", "label": "Origami", "prompt": "origami paper craft, folded paper, crisp creases"},
        {"id": "clay", "label": "Clay / stop-motion", "prompt": "claymation stop-motion, tactile sculpted forms"},
        {"id": "pixel", "label": "Pixel art", "prompt": "pixel art style, retro 16-bit aesthetic"},
        {"id": "neon", "label": "Neon cyberpunk", "prompt": "neon-lit cyberpunk, glowing edges, rain-slick streets"},
    ],
    "tones": [
        {"id": "", "label": "Neutral"},
        {"id": "somber", "label": "Somber", "prompt": "somber mood, muted palette, subdued lighting"},
        {"id": "calm", "label": "Calm", "prompt": "calm peaceful tone, soft warm light"},
        {"id": "energetic", "label": "Energetic", "prompt": "high energy, dynamic motion, bright contrast"},
        {"id": "hilarious", "label": "Hilarious", "prompt": "comedic exaggerated tone, playful bright colors"},
    ],
}

_PROMPT_BY_GROUP: dict[str, dict[str, str]] = {
    group: {item["id"]: item.get("prompt", "") for item in items if item["id"]}
    for group, items in LOOK_CATALOG.items()
}


class VisualLook(BaseModel):
    visual_style: Annotated[str, Field(description="Visual style preset id.")] = ""
    visual_material: Annotated[str, Field(description="Material / medium preset id.")] = ""
    visual_tone: Annotated[str, Field(description="Mood / tone preset id.")] = ""

    def is_empty(self) -> bool:
        return not (self.visual_style or self.visual_material or self.visual_tone)

    def prompt_suffix(self) -> str:
        parts: list[str] = []
        for group, value in (
            ("styles", self.visual_style),
            ("materials", self.visual_material),
            ("tones", self.visual_tone),
        ):
            if not value:
                continue
            phrase = _PROMPT_BY_GROUP.get(group, {}).get(value, "")
            if phrase:
                parts.append(phrase)
        return ", ".join(parts)

    def planner_hint(self) -> str:
        """Short hint for the storyboard LLM (search_terms should match this look)."""
        if self.is_empty():
            return ""
        labels: list[str] = []
        for group, value in (
            ("styles", self.visual_style),
            ("materials", self.visual_material),
            ("tones", self.visual_tone),
        ):
            if not value:
                continue
            for item in LOOK_CATALOG[group]:
                if item["id"] == value:
                    labels.append(item["label"])
                    break
        return f"Visual direction for AI footage: {', '.join(labels)}. Match search_terms to this look."


def is_ai_stock_provider(name: str) -> bool:
    return name.strip().lower() in AI_STOCK_PROVIDERS


def apply_visual_look_to_query(query: str, look: VisualLook, stock_provider: str) -> str:
    """Append look phrases to stock/AI search prompts when using generative footage."""
    base = query.strip()
    if not is_ai_stock_provider(stock_provider) or look.is_empty():
        return base
    suffix = look.prompt_suffix()
    if not suffix:
        return base
    return f"{base}, {suffix}" if base else suffix
