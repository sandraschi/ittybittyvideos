"""Tests for R10 prompt director trope loading and prompt enrichment."""

from videogen_mcp.providers.llm_openai import SYSTEM_PROMPT, build_short_script_messages
from videogen_mcp.services.prompt_director import (
    enrich_for_planner,
    enrich_for_short_script,
    list_structures,
    load_trope,
    normalize_structure_id,
)


def test_normalize_structure_id():
    assert normalize_structure_id("") is None
    assert normalize_structure_id("trope:pet-food-duo-review") == "pet-food-duo-review"
    assert normalize_structure_id("countdown-three-things") == "countdown-three-things"


def test_load_pet_food_trope():
    trope = load_trope("pet-food-duo-review")
    assert trope is not None
    assert trope.id == "pet-food-duo-review"
    assert len(trope.beats) >= 3
    assert "Yummy" in str(trope.visual.get("text_overlays", []))


def test_list_structures_includes_seeds():
    items = list_structures()
    ids = {s["trope_id"] for s in items}
    assert "pet-food-duo-review" in ids
    assert "dog-tease-fridge" in ids


def test_enrich_short_script_injects_beats():
    system, user = enrich_for_short_script(
        SYSTEM_PROMPT,
        "Two shepherds taste test",
        4,
        "en",
        "trope:pet-food-duo-review",
        "Use on-screen Yummy / Whazzat labels",
    )
    assert "pet-food-duo-review" in system
    assert "Beat outline" in system
    assert "Yummy" in system
    assert "Style notes:" in user


def test_enrich_short_script_unchanged_without_structure():
    system, user = enrich_for_short_script(SYSTEM_PROMPT, "Cats", 3, "en", "", "")
    assert system == SYSTEM_PROMPT
    assert user.startswith("Topic: Cats")


def test_build_short_script_messages():
    msgs = build_short_script_messages(
        "Dog snacks",
        4,
        structure="trope:duo-unfair-portion",
    )
    assert msgs[0]["role"] == "system"
    assert "duo-unfair-portion" in msgs[0]["content"]


def test_enrich_planner_mid_chapters():
    base_user = "Topic: GSD feeding\nVideo type: showcase\n"
    system, user = enrich_for_planner(
        "PLANNER",
        base_user,
        "trope:pet-food-duo-review",
        "Vertical 9:16",
    )
    assert "Suggested chapter arc" in system
    assert "Meet the picky" in system or "Round 1" in system
