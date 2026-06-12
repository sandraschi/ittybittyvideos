"""R10 prompt director — load trope YAML and enrich LLM script/planner prompts."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml
from loguru import logger

from videogen_mcp.models.trope import TropeTemplate


def trope_dir() -> Path:
    """Dev: repo templates/tropes. Wheel: videogen_mcp/tropes (hatch force-include)."""
    bundled = Path(__file__).resolve().parent.parent / "tropes"
    if bundled.is_dir():
        return bundled
    for parent in Path(__file__).resolve().parents:
        candidate = parent / "templates" / "tropes"
        if candidate.is_dir():
            return candidate
    return Path(__file__).resolve().parents[3] / "templates" / "tropes"


def normalize_structure_id(structure: str | None) -> str | None:
    if not structure or not structure.strip():
        return None
    raw = structure.strip()
    if raw.startswith("trope:"):
        return raw[6:].strip() or None
    return raw


@lru_cache(maxsize=64)
def load_trope(trope_id: str) -> TropeTemplate | None:
    path = trope_dir() / f"{trope_id}.yaml"
    if not path.is_file():
        logger.warning(f"Trope template not found: {trope_id} ({path})")
        return None
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        return TropeTemplate.model_validate(data)
    except Exception as e:
        logger.warning(f"Failed to load trope {trope_id}: {e}")
        return None


def list_structures() -> list[dict]:
    out: list[dict] = []
    root = trope_dir()
    if not root.is_dir():
        return out
    for path in sorted(root.glob("*.yaml")):
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            tid = str(data.get("id") or path.stem)
            out.append(
                {
                    "id": f"trope:{tid}",
                    "trope_id": tid,
                    "label": data.get("label") or tid,
                    "video_types": data.get("video_types") or [],
                    "exemplar_views": data.get("exemplar_views") or "",
                    "beat_count": len(data.get("beats") or []),
                }
            )
        except Exception as e:
            logger.warning(f"Skipping trope file {path.name}: {e}")
    return out


def _beat_block(trope: TropeTemplate, *, mid: bool) -> str:
    lines = [f"Narrative structure: {trope.label} ({trope.id})"]
    if trope.exemplar_views:
        lines.append(f"Reference format (views): {trope.exemplar_views}")
    if trope.example_hook:
        lines.append(f"Example hook: {trope.example_hook}")

    chapters = trope.expand_to_mid.get("chapters") if mid else None
    if chapters:
        lines.append("Suggested chapter arc:")
        for i, title in enumerate(chapters, 1):
            lines.append(f"  {i}. {title}")

    if trope.beats:
        lines.append("Beat outline (follow this order and intent):")
        for i, beat in enumerate(trope.beats, 1):
            lines.append(f"  {i}. [{beat.scene_type}] {beat.narration_goal} (~{beat.duration_hint}s)")

    vis = trope.visual
    overlays = vis.get("text_overlays") if vis else None
    if overlays:
        lines.append(f"On-screen text cues: {', '.join(overlays)}")
    cut = vis.get("cut_every_seconds") if vis else None
    if cut:
        lines.append(f"Target cut pace: ~every {cut}s")

    return "\n".join(lines)


def enrich_for_short_script(
    base_system: str,
    topic: str,
    paragraph_count: int,
    language: str,
    structure: str,
    style_notes: str,
) -> tuple[str, str]:
    user = f"Topic: {topic}\nSegments: {paragraph_count}\nLanguage: {language}"
    if style_notes.strip():
        user += f"\nStyle notes: {style_notes.strip()}"

    trope_id = normalize_structure_id(structure)
    if not trope_id:
        return base_system, user

    trope = load_trope(trope_id)
    if not trope:
        return base_system, user

    block = _beat_block(trope, mid=False)
    system = (
        f"{base_system}\n\n{block}\n\n"
        "Follow the beat outline. Map beats to segments when segment count allows. "
        "First segment must work as a 3-second hook."
    )
    return system, user


def enrich_for_planner(
    base_system: str,
    user_prompt: str,
    structure: str,
    style_notes: str,
) -> tuple[str, str]:
    trope_id = normalize_structure_id(structure)
    if not trope_id:
        return base_system, user_prompt

    trope = load_trope(trope_id)
    if not trope:
        return base_system, user_prompt

    block = _beat_block(trope, mid=True)
    system = (
        f"{base_system}\n\n{block}\n\n"
        "Expand beats into chapters and scenes. Use suggested chapter titles when provided. "
        "Keep hook scene first; honor text overlay cues in scene notes where relevant."
    )
    if style_notes.strip() and "Style notes:" not in user_prompt:
        user_prompt = f"{user_prompt.rstrip()}\nStyle notes: {style_notes.strip()}\n"
    return system, user_prompt
