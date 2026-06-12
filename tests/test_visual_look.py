"""Tests for AI footage visual look prompt suffixes."""

from videogen_mcp.models.visual_look import (
    VisualLook,
    apply_visual_look_to_query,
    is_ai_stock_provider,
)


def test_is_ai_stock_provider():
    assert is_ai_stock_provider("localgen")
    assert is_ai_stock_provider("veo")
    assert not is_ai_stock_provider("pexels")


def test_apply_suffix_for_localgen():
    look = VisualLook(visual_style="cinematic", visual_material="origami", visual_tone="somber")
    out = apply_visual_look_to_query("cat on windowsill", look, "localgen")
    assert out.startswith("cat on windowsill,")
    assert "origami" in out.lower()
    assert "somber" in out.lower()


def test_pexels_unchanged():
    look = VisualLook(visual_material="oil_paint", visual_tone="hilarious")
    out = apply_visual_look_to_query("sunset beach", look, "pexels")
    assert out == "sunset beach"


def test_empty_look():
    look = VisualLook()
    assert look.prompt_suffix() == ""
    assert apply_visual_look_to_query("query", look, "veo") == "query"
