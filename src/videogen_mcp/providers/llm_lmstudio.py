from __future__ import annotations

from loguru import logger
from openai import AsyncOpenAI

from videogen_mcp.config import get_settings
from videogen_mcp.providers import register_llm
from videogen_mcp.providers.llm_openai import OpenAILLMProvider, _parse_script_json, build_short_script_messages


@register_llm("lmstudio")
class LMStudioLLMProvider(OpenAILLMProvider):
    async def _client(self) -> AsyncOpenAI:
        settings = get_settings()
        return AsyncOpenAI(
            api_key=settings.lmstudio_api_key or "lm-studio",
            base_url=settings.lmstudio_base_url,
        )

    async def _resolve_model(self, client: AsyncOpenAI) -> str:
        settings = get_settings()
        if settings.lmstudio_model.strip():
            return settings.lmstudio_model.strip()
        models = await client.models.list()
        if models.data:
            return models.data[0].id
        raise ValueError("LM Studio has no model loaded. Open LM Studio, load a model, and enable the local server.")

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
        client = await self._client()
        model = await self._resolve_model(client)
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

    async def health_check(self) -> bool:
        try:
            client = await self._client()
            await client.models.list()
            return True
        except Exception as e:
            logger.warning(f"LM Studio health check failed: {e}")
            return False

    async def loaded_model(self) -> str | None:
        try:
            client = await self._client()
            return await self._resolve_model(client)
        except (ValueError, OSError):
            return None
