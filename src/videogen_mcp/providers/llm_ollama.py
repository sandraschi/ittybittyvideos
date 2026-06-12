from __future__ import annotations

from loguru import logger
from openai import AsyncOpenAI

from videogen_mcp.config import get_settings
from videogen_mcp.providers import register_llm
from videogen_mcp.providers.llm_openai import OpenAILLMProvider, _parse_script_json, build_short_script_messages


@register_llm("ollama")
class OllamaLLMProvider(OpenAILLMProvider):
    async def generate_script(
        self,
        topic: str,
        paragraph_count: int,
        language: str = "en",
        *,
        structure: str = "",
        style_notes: str = "",
        intro: str = "",
    ) -> dict:
        settings = get_settings()
        client = AsyncOpenAI(api_key="ollama", base_url=settings.ollama_base_url)
        model = await self._resolve_model(client, settings.ollama_model)
        resp = await client.chat.completions.create(
            model=model,
            messages=build_short_script_messages(
                topic,
                paragraph_count,
                language,
                structure=structure,
                style_notes=style_notes,
                intro=intro,
            ),
            temperature=0.8,
            max_tokens=2000,
        )
        raw = resp.choices[0].message.content or ""
        return _parse_script_json(raw)

    async def _resolve_model(self, client: AsyncOpenAI, configured: str) -> str:
        if configured.strip():
            return configured.strip()
        models = await client.models.list()
        if models.data:
            return models.data[0].id
        return "llama3.2:3b"

    async def health_check(self) -> bool:
        try:
            settings = get_settings()
            client = AsyncOpenAI(api_key="ollama", base_url=settings.ollama_base_url)
            await client.models.list()
            return True
        except Exception as e:
            logger.warning(f"Ollama health check failed: {e}")
            return False
