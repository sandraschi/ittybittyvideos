"""Plugin provider registry. Each provider is a module — no monolith router."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from videogen_mcp.providers.base import LLMProvider, StockProvider, TTSProvider

_llm_registry: dict[str, type[LLMProvider]] = {}
_stock_registry: dict[str, type[StockProvider]] = {}
_tts_registry: dict[str, type[TTSProvider]] = {}


def register_llm(name: str):
    def decorator(cls: type[LLMProvider]):
        _llm_registry[name] = cls
        return cls

    return decorator


def register_stock(name: str):
    def decorator(cls: type[StockProvider]):
        _stock_registry[name] = cls
        return cls

    return decorator


def register_tts(name: str):
    def decorator(cls: type[TTSProvider]):
        _tts_registry[name] = cls
        return cls

    return decorator


def get_llm(name: str | None = None) -> LLMProvider:
    import videogen_mcp.providers.llm_deepseek  # noqa: F401
    import videogen_mcp.providers.llm_lmstudio  # noqa: F401
    import videogen_mcp.providers.llm_ollama  # noqa: F401
    import videogen_mcp.providers.llm_openai  # noqa: F401
    import videogen_mcp.providers.llm_qwen  # noqa: F401
    from videogen_mcp.config import get_settings

    key = name or get_settings().videogen_llm_provider
    if key not in _llm_registry:
        raise ValueError(f"Unknown LLM provider: {key}. Available: {list(_llm_registry)}")
    return _llm_registry[key]()


def get_stock(name: str | None = None) -> StockProvider:
    import videogen_mcp.providers.stock_localgen  # noqa: F401
    import videogen_mcp.providers.stock_pexels  # noqa: F401
    from videogen_mcp.config import get_settings

    if "cogvideo" not in _stock_registry and "localgen" in _stock_registry:
        _stock_registry["cogvideo"] = _stock_registry["localgen"]

    key = name or get_settings().videogen_stock_provider
    if key not in _stock_registry:
        raise ValueError(f"Unknown stock provider: {key}. Available: {list(_stock_registry)}")
    return _stock_registry[key]()


def get_tts(name: str | None = None) -> TTSProvider:
    import videogen_mcp.providers.tts_cosyvoice  # noqa: F401
    import videogen_mcp.providers.tts_edge  # noqa: F401
    from videogen_mcp.config import get_settings

    key = name or get_settings().videogen_tts_provider
    if key not in _tts_registry:
        raise ValueError(f"Unknown TTS provider: {key}. Available: {list(_tts_registry)}")
    return _tts_registry[key]()


def list_providers() -> dict[str, list[str]]:
    import videogen_mcp.providers.llm_deepseek  # noqa: F401
    import videogen_mcp.providers.llm_lmstudio  # noqa: F401
    import videogen_mcp.providers.llm_ollama  # noqa: F401
    import videogen_mcp.providers.llm_openai  # noqa: F401
    import videogen_mcp.providers.llm_qwen  # noqa: F401
    import videogen_mcp.providers.stock_localgen  # noqa: F401
    import videogen_mcp.providers.stock_pexels  # noqa: F401
    import videogen_mcp.providers.tts_cosyvoice  # noqa: F401
    import videogen_mcp.providers.tts_edge  # noqa: F401

    if "cogvideo" not in _stock_registry and "localgen" in _stock_registry:
        _stock_registry["cogvideo"] = _stock_registry["localgen"]

    return {
        "llm": list(_llm_registry),
        "stock": list(_stock_registry),
        "tts": list(_tts_registry),
    }
