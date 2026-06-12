from __future__ import annotations

import json
import re

from loguru import logger
from openai import AsyncOpenAI

from videogen_mcp.config import get_settings
from videogen_mcp.providers import register_llm
from videogen_mcp.providers.base import LLMProvider

SYSTEM_PROMPT = """You are a short-video script writer. Given a topic, produce a JSON object with:
- "title": catchy video title (5-10 words)
- "segments": array of objects, each with:
  - "narration": 2-3 sentences of narration text (natural speech, no markdown, no labels)
  - "search_terms": array of 2-3 stock footage search keywords for this segment

Match the language of the narration to the topic language.
Return ONLY valid JSON, no markdown fences, no explanation."""


@register_llm("openai")
class OpenAILLMProvider(LLMProvider):
    async def generate_script(self, topic: str, paragraph_count: int, language: str = "en") -> dict:
        settings = get_settings()
        if not settings.openai_api_key.strip():
            raise ValueError(
                "OPENAI_API_KEY is not set. Add it to .env, use Ollama, or pass a custom script."
            )
        client = AsyncOpenAI(api_key=settings.openai_api_key, base_url=settings.openai_base_url)
        resp = await client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Topic: {topic}\nSegments: {paragraph_count}\nLanguage: {language}"},
            ],
            temperature=0.8,
            max_tokens=2000,
        )
        raw = resp.choices[0].message.content or ""
        return _parse_script_json(raw)

    async def health_check(self) -> bool:
        settings = get_settings()
        if not settings.openai_api_key:
            return False
        try:
            client = AsyncOpenAI(api_key=settings.openai_api_key, base_url=settings.openai_base_url)
            await client.models.list()
            return True
        except Exception as e:
            logger.warning(f"OpenAI health check failed: {e}")
            return False


def _parse_script_json(raw: str) -> dict:
    raw = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL).strip()
    think_open = "<" + "think" + ">"
    think_close = "<" + "/" + "think" + ">"
    raw = re.sub(re.escape(think_open) + r"[\s\S]*?" + re.escape(think_close), "", raw).strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            return json.loads(match.group())
        raise ValueError(f"Could not parse LLM response as JSON: {raw[:200]}")
