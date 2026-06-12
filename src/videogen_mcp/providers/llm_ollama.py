from __future__ import annotations

from loguru import logger
from openai import AsyncOpenAI

from videogen_mcp.providers import register_llm
from videogen_mcp.providers.llm_openai import OpenAILLMProvider


@register_llm("ollama")
class OllamaLLMProvider(OpenAILLMProvider):
    async def generate_script(self, topic: str, paragraph_count: int, language: str = "en") -> dict:
        from videogen_mcp.providers.llm_openai import SYSTEM_PROMPT, _parse_script_json

        client = AsyncOpenAI(api_key="ollama", base_url="http://localhost:11434/v1")
        resp = await client.chat.completions.create(
            model="llama3.2:3b",
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
        try:
            client = AsyncOpenAI(api_key="ollama", base_url="http://localhost:11434/v1")
            await client.models.list()
            return True
        except Exception as e:
            logger.warning(f"Ollama health check failed: {e}")
            return False
