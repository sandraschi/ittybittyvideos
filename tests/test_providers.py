import pytest

from videogen_mcp.providers import list_providers


def test_list_providers_returns_all_types():
    providers = list_providers()
    assert "llm" in providers
    assert "stock" in providers
    assert "tts" in providers


def test_openai_registered():
    providers = list_providers()
    assert "openai" in providers["llm"]


def test_ollama_registered():
    providers = list_providers()
    assert "ollama" in providers["llm"]


def test_pexels_registered():
    providers = list_providers()
    assert "pexels" in providers["stock"]


def test_pixabay_registered():
    providers = list_providers()
    assert "pixabay" in providers["stock"]


def test_coverr_registered():
    providers = list_providers()
    assert "coverr" in providers["stock"]


def test_mixkit_registered():
    providers = list_providers()
    assert "mixkit" in providers["stock"]


def test_nasa_registered():
    providers = list_providers()
    assert "nasa" in providers["stock"]


def test_localgen_registered():
    providers = list_providers()
    assert "localgen" in providers["stock"]
    assert "cogvideo" in providers["stock"]
    assert "veo" in providers["stock"]
    assert "omni" in providers["stock"]


def test_localgen_prompt_parse():
    from videogen_mcp.providers.stock_localgen import _aspect_from_clip_url, _prompt_from_clip_url

    url = "localgen://generate?prompt=dog%20running&aspect=9%3A16"
    assert _prompt_from_clip_url(url) == "dog running"
    assert _aspect_from_clip_url(url) == "9:16"


def test_cogvideo_registered():
    providers = list_providers()
    assert "cogvideo" in providers["stock"]


def test_cogvideo_prompt_parse():
    from videogen_mcp.providers.stock_localgen import _aspect_from_clip_url, _prompt_from_clip_url

    url = "cogvideo://generate?prompt=dog%20running&aspect=9%3A16"
    assert _prompt_from_clip_url(url) == "dog running"
    assert _aspect_from_clip_url(url) == "9:16"


def test_edge_tts_registered():
    providers = list_providers()
    assert "edge-tts" in providers["tts"]


def test_lmstudio_registered():
    providers = list_providers()
    assert "lmstudio" in providers["llm"]


def test_deepseek_registered():
    providers = list_providers()
    assert "deepseek" in providers["llm"]


def test_unknown_provider_raises():
    from videogen_mcp.providers import get_llm

    with pytest.raises(ValueError, match="Unknown LLM provider"):
        get_llm("nonexistent_provider_xyz")


def test_llm_openai_parse_json():
    from videogen_mcp.providers.llm_openai import _parse_script_json

    raw = '```json\n{"title": "Test", "segments": []}\n```'
    result = _parse_script_json(raw)
    assert result["title"] == "Test"


def test_llm_openai_parse_with_think_tags():
    from videogen_mcp.providers.llm_openai import _parse_script_json

    raw = '<think>reasoning here</think>{"title": "Clean", "segments": []}'
    result = _parse_script_json(raw)
    assert result["title"] == "Clean"
