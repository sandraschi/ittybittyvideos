"""Tests for intro sequence packs and prompt injection."""

from videogen_mcp.services.intros import intro_prompt_block, list_intro_packs, load_intro_pack
from videogen_mcp.services.prompt_director import enrich_for_short_script, load_trope


def test_alpine_mariachi_contrast():
    pack = load_intro_pack("alpine-mariachi-contrast")
    assert pack is not None
    assert "mariachi" in pack.audio.get("music", "").lower()
    text = intro_prompt_block("alpine-mariachi-contrast", seed=2)
    assert "alpine" in text.lower() or "Alps" in text
    assert "mariachi" in text.lower()


def test_all_contrast_packs_load():
    ids = [
        "bluey-horror-contrast",
        "alpine-mariachi-contrast",
        "asmr-demolition-contrast",
        "nature-doc-toddler-chaos",
        "elevator-jazz-fall",
        "ikea-inspirational-piano",
        "deadpan-corporate",
        "documentary-gravitas",
        "epic-trailer",
    ]
    for pid in ids:
        pack = load_intro_pack(pid)
        assert pack is not None, pid
        block = intro_prompt_block(pid, seed=1)
        assert len(block) > 80, pid


def test_ikea_inspirational_screw():
    text = intro_prompt_block("ikea-inspirational-piano", seed=3)
    assert "screw" in text.lower() or "IKEA" in text or "flat-pack" in text.lower()
    assert "inspirational" in text.lower() or "piano" in text.lower()


def test_list_intro_packs():
    packs = list_intro_packs()
    ids = {p["id"] for p in packs}
    assert "bluey-horror-contrast" in ids
    assert "alpine-mariachi-contrast" in ids
    assert "ikea-inspirational-piano" in ids
    assert "documentary-gravitas" in ids


def test_bluey_horror_contrast_audio():
    pack = load_intro_pack("bluey-horror-contrast")
    assert pack is not None
    assert pack.tone == "hilarious_contrast"
    assert "horror" in pack.audio.get("music", "").lower()


def test_intro_block_contrast_rule():
    text = intro_prompt_block("bluey-horror-contrast", seed=1)
    assert "horror" in text.lower()
    assert "Saturday morning" in text or "contrast" in text.lower()


def test_contrast_intro_trope():
    trope = load_trope("contrast-intro-sequence")
    assert trope is not None
    assert trope.intro.get("pack") == "bluey-horror-contrast"


def test_enrich_with_intro_only():
    system, _ = enrich_for_short_script(
        "BASE",
        "Dog playdate",
        5,
        "en",
        "",
        "",
        "intro:bluey-horror-contrast",
    )
    assert "horror" in system.lower()
    assert "Intro sequence" in system


def test_enrich_trope_plus_override_intro():
    system, _ = enrich_for_short_script(
        "BASE",
        "Corporate training",
        5,
        "en",
        "trope:contrast-intro-sequence",
        "",
        "intro:deadpan-corporate",
    )
    assert "deadpan" in system.lower() or "corporate" in system.lower()
