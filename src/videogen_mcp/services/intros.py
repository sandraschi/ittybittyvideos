"""Intro sequence packs — serious opens and hilarious visual/audio contrast."""

from __future__ import annotations

import random
from functools import lru_cache
from pathlib import Path

import yaml
from loguru import logger

from videogen_mcp.models.intro import IntroPack


def intros_dir() -> Path:
    bundled = Path(__file__).resolve().parent.parent / "intros"
    if bundled.is_dir():
        return bundled
    for parent in Path(__file__).resolve().parents:
        candidate = parent / "templates" / "intros"
        if candidate.is_dir():
            return candidate
    return Path(__file__).resolve().parents[3] / "templates" / "intros"


def normalize_intro_id(intro: str | None) -> str | None:
    if not intro or not intro.strip():
        return None
    raw = intro.strip()
    if raw.startswith("intro:"):
        return raw[6:].strip() or None
    return raw


@lru_cache(maxsize=16)
def load_intro_pack(pack_id: str) -> IntroPack | None:
    path = intros_dir() / f"{pack_id}.yaml"
    if not path.is_file():
        logger.warning(f"Intro pack not found: {pack_id}")
        return None
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        return IntroPack.model_validate(data)
    except Exception as e:
        logger.warning(f"Failed to load intro pack {pack_id}: {e}")
        return None


def list_intro_packs() -> list[dict]:
    root = intros_dir()
    if not root.is_dir():
        return []
    out: list[dict] = []
    for path in sorted(root.glob("*.yaml")):
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            pid = str(data.get("id") or path.stem)
            out.append(
                {
                    "id": pid,
                    "intro_id": f"intro:{pid}",
                    "label": data.get("label") or pid,
                    "tone": data.get("tone") or "",
                    "duration_hint": data.get("duration_hint"),
                }
            )
        except Exception as e:
            logger.warning(f"Skipping intro pack {path.name}: {e}")
    return out


def intro_prompt_block(pack_id: str, *, seed: int | None = None) -> str:
    pack = load_intro_pack(pack_id)
    if not pack:
        return ""

    rng = random.Random(seed)
    lines = [
        f"Intro sequence: {pack.label} ({pack.id}) — tone: {pack.tone}",
        pack.description.strip(),
        f"Target intro duration: ~{pack.duration_hint}s before main hook.",
    ]

    vis = pack.visual
    if vis.get("style"):
        lines.append(f"Visual: {vis['style']}")
    if vis.get("avoid"):
        lines.append(f"Visual avoid: {vis['avoid']}")
    if vis.get("search_terms"):
        lines.append(f"Intro footage search: {', '.join(vis['search_terms'])}")

    aud = pack.audio
    if aud.get("music"):
        lines.append(f"Audio/music (critical): {aud['music']}")
    if aud.get("sfx"):
        lines.append(f"SFX: {aud['sfx']}")
    if aud.get("contrast_line"):
        lines.append(f"Contrast rule: {aud['contrast_line']}")
    if aud.get("bgm_tags"):
        lines.append(f"BGM tags for editor: {', '.join(aud['bgm_tags'])}")

    if pack.structure:
        lines.append("Intro beat structure:")
        for i, step in enumerate(pack.structure, 1):
            lines.append(f"  {i}. {step}")

    narr = pack.narration
    if narr.get("mode"):
        lines.append(f"Narration mode: {narr['mode']}")
    examples = list(narr.get("examples") or pack.example_lines)
    if examples:
        lines.append(f"Example intro line: {rng.choice(examples)}")

    if pack.post_intro:
        lines.append(f"After intro: {pack.post_intro}")

    lines.append(
        "Put intro in first segment(s) or dedicated intro scene. "
        "Describe audio/SFX in segment narration notes — pipeline BGM is separate; "
        "flag contrast for human or future sfx layer."
    )
    return "\n".join(lines)


def intro_prompt_for_trope(intro_config: dict | None) -> str:
    if not intro_config:
        return ""
    pack_id = intro_config.get("pack") or intro_config.get("pack_id")
    if not pack_id:
        return ""
    return intro_prompt_block(str(pack_id))


def resolve_intro_pack(intro: str, trope_intro: dict | None) -> str | None:
    """Standalone intro param wins; else trope.embedded intro pack."""
    pid = normalize_intro_id(intro)
    if pid:
        return pid
    if trope_intro:
        return trope_intro.get("pack") or trope_intro.get("pack_id")
    return None
