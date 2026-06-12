"""Tests for absurd credits corpus and trope injection."""

from videogen_mcp.services.credits import (
    build_contributor_roll,
    credits_prompt_for_trope,
    load_credits_pack,
    sample_credits_block,
)
from videogen_mcp.services.prompt_director import enrich_for_short_script, load_trope


def test_load_absurd_pixar_pack():
    pack = load_credits_pack("absurd-pixar")
    assert pack is not None
    names = {e.name for e in pack.featured}
    assert "Albert Einstein" in names
    assert "Attila the Hun" in names


def test_roll_includes_featured():
    roll = build_contributor_roll("absurd-pixar", count=50, seed=42)
    names = {e.name for e in roll}
    assert "Albert Einstein" in names
    assert "Attila the Hun" in names
    assert len(roll) >= 48


def test_sample_block_mentions_post_credits():
    text = sample_credits_block("absurd-pixar", line_count=12, seed=1, post_credits=True)
    assert "Einstein" in text
    assert "Post-credits" in text


def test_credits_trope_injects_into_prompt():
    trope = load_trope("absurd-credits-roll")
    assert trope is not None
    assert trope.credits.get("pack") == "absurd-pixar"

    block = credits_prompt_for_trope(trope.credits)
    assert "Strategy Consultant" in block

    system, _ = enrich_for_short_script(
        "BASE",
        "Dog video",
        6,
        "en",
        "trope:absurd-credits-roll",
        "",
    )
    assert "Albert Einstein" in system
    assert "post-credits" in system.lower()
