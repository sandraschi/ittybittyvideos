"""Qwen 3 LLM provider -- DashScope API or local Ollama.

Qwen 3 (Alibaba/Tongyi) is the strongest Chinese open-weight LLM family.
Supports both cloud (DashScope) and local (Ollama qwen3:8b) inference.
"""

from __future__ import annotations

import os

from loguru import logger
from openai import AsyncOpenAI

from videogen_mcp.providers import register_llm
from videogen_mcp.providers.llm_openai import OpenAILLMProvider, _parse_script_json, build_short_script_messages


@register_llm("qwen")
class QwenLLMProvider(OpenAILLMProvider):
    async def generate_script(
        self,
        topic: str,
        paragraph_count: int,
        language: str = "zh",
        *,
        structure: str = "",
        style_notes: str = "",
    ) -> dict:
        api_key = os.environ.get("DASHSCOPE_API_KEY", "")
        if api_key:
            base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
            model = os.environ.get("QWEN_MODEL", "qwen-plus")
        else:
            base_url = "http://localhost:11434/v1"
            api_key = "ollama"
            model = os.environ.get("QWEN_MODEL", "qwen3:8b")

        client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        resp = await client.chat.completions.create(
            model=model,
            messages=build_short_script_messages(
                topic, paragraph_count, language, structure=structure, style_notes=style_notes
            ),
            temperature=0.8,
            max_tokens=2000,
        )
        raw = resp.choices[0].message.content or ""
        return _parse_script_json(raw)

    async def health_check(self) -> bool:
        api_key = os.environ.get("DASHSCOPE_API_KEY", "")
        if api_key:
            base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
        else:
            base_url = "http://localhost:11434/v1"
            api_key = "ollama"
        try:
            client = AsyncOpenAI(api_key=api_key, base_url=base_url)
            await client.models.list()
            return True
        except Exception as e:
            logger.warning(f"Qwen health check failed: {e}")
            return False
