"""Absurd end-credits corpus — Pixar-style contributor rolls for LLM + future FFmpeg scroll."""

from __future__ import annotations

import random
from functools import lru_cache
from pathlib import Path

import yaml
from loguru import logger

from videogen_mcp.models.credits import CreditEntry, CreditsPack


def credits_dir() -> Path:
    bundled = Path(__file__).resolve().parent.parent / "credits"
    if bundled.is_dir():
        return bundled
    for parent in Path(__file__).resolve().parents:
        candidate = parent / "templates" / "credits"
        if candidate.is_dir():
            return candidate
    return Path(__file__).resolve().parents[3] / "templates" / "credits"


@lru_cache(maxsize=16)
def load_credits_pack(pack_id: str) -> CreditsPack | None:
    path = credits_dir() / f"{pack_id}.yaml"
    if not path.is_file():
        logger.warning(f"Credits pack not found: {pack_id}")
        return None
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        return CreditsPack.model_validate(data)
    except Exception as e:
        logger.warning(f"Failed to load credits pack {pack_id}: {e}")
        return None


def list_credits_packs() -> list[dict]:
    root = credits_dir()
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
                    "label": data.get("label") or pid,
                    "featured_count": len(data.get("featured") or []),
                    "pool_count": len(data.get("pool") or []),
                }
            )
        except Exception as e:
            logger.warning(f"Skipping credits pack {path.name}: {e}")
    return out


def build_contributor_roll(
    pack_id: str,
    *,
    count: int | None = None,
    seed: int | None = None,
) -> list[CreditEntry]:
    pack = load_credits_pack(pack_id)
    if not pack:
        return []

    rng = random.Random(seed)
    target = count if count is not None else min(pack.max_contributors, max(pack.min_contributors, 60))
    target = max(pack.min_contributors, min(target, pack.max_contributors))

    roll: list[CreditEntry] = list(pack.featured)
    seen = {e.name.lower() for e in roll}

    pool = list(pack.pool)
    rng.shuffle(pool)
    for entry in pool:
        if len(roll) >= target:
            break
        if entry.name.lower() in seen:
            continue
        roll.append(entry)
        seen.add(entry.name.lower())

    filler_idx = 1
    templates = pack.filler_templates or ["Additional Crew Member #{n}"]
    while len(roll) < target:
        tpl = rng.choice(templates)
        name = tpl.format(n=filler_idx)
        roll.append(CreditEntry(name=name, role=rng.choice(pack.departments) if pack.departments else "Uncredited"))
        filler_idx += 1

    return roll


def format_roll_text(
    roll: list[CreditEntry],
    *,
    max_lines: int | None = None,
    include_departments: bool = True,
    departments: list[str] | None = None,
) -> str:
    lines: list[str] = []
    if include_departments and departments:
        for dept in departments:
            lines.append(f"--- {dept} ---")
    for entry in roll[: max_lines or len(roll)]:
        lines.append(f"{entry.name} — {entry.role}")
    return "\n".join(lines)


def sample_credits_block(
    pack_id: str,
    *,
    line_count: int = 24,
    seed: int | None = None,
    post_credits: bool = False,
) -> str:
    """Text block for LLM prompts — sample of the full absurd roll."""
    pack = load_credits_pack(pack_id)
    if not pack:
        return ""

    rng = random.Random(seed)
    roll = build_contributor_roll(pack_id, count=max(line_count, pack.min_contributors), seed=seed)
    dept_sample = list(pack.departments)
    rng.shuffle(dept_sample)
    dept_sample = dept_sample[: min(4, len(dept_sample))]

    header = (
        f"Absurd credits roll ({pack.label}): aim for {pack.min_contributors}+ joke contributors total.\n"
        "Featured names MUST appear:\n"
    )
    featured_lines = "\n".join(f"  • {e.name} — {e.role}" for e in pack.featured[:10])
    body = format_roll_text(roll, max_lines=line_count, include_departments=True, departments=dept_sample)

    block = f"{header}{featured_lines}\n\nSample scroll lines (generate more in this voice):\n{body}"

    if post_credits and pack.post_credits_stingers:
        stinger = rng.choice(pack.post_credits_stingers)
        block += f"\n\nPost-credits stinger (after THE END): {stinger}"
    return block


def credits_prompt_for_trope(trope_credits: dict | None) -> str:
    if not trope_credits:
        return ""
    pack_id = trope_credits.get("pack") or trope_credits.get("pack_id")
    if not pack_id:
        return ""
    lines = int(trope_credits.get("min_lines") or 20)
    post = bool(trope_credits.get("post_credits"))
    return sample_credits_block(str(pack_id), line_count=lines, post_credits=post)
