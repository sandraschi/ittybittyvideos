from __future__ import annotations

from loguru import logger
from openai import AsyncOpenAI

from videogen_mcp.config import get_settings
from videogen_mcp.providers import register_llm
from videogen_mcp.providers.llm_openai import LLMProvider, _parse_script_json, build_short_script_messages


@register_llm("deepseek")
class DeepSeekLLMProvider(LLMProvider):
    async def generate_script(
        self,
        topic: str,
        paragraph_count: int,
        language: str = "en",
        *,
        structure: str = "",
        style_notes: str = "",
    ) -> dict:
        settings = get_settings()
        if not settings.deepseek_api_key.strip():
            raise ValueError("DEEPSEEK_API_KEY is not set. Add it to .env and restart the backend.")

        client = AsyncOpenAI(
            api_key=settings.deepseek_api_key,
            base_url=settings.deepseek_base_url,
        )
        resp = await client.chat.completions.create(
            model=settings.deepseek_model,
            messages=build_short_script_messages(
                topic, paragraph_count, language, structure=structure, style_notes=style_notes
            ),
            temperature=0.8,
            max_tokens=2000,
        )
        raw = resp.choices[0].message.content or ""
        return _parse_script_json(raw)

    async def health_check(self) -> bool:
        settings = get_settings()
        if not settings.deepseek_api_key.strip():
            return False
        try:
            client = AsyncOpenAI(
                api_key=settings.deepseek_api_key,
                base_url=settings.deepseek_base_url,
            )
            await client.models.list()
            return True
        except Exception as e:
            logger.warning(f"DeepSeek health check failed: {e}")
            return False
