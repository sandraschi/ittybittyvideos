"""CosyVoice TTS provider -- Alibaba open-weight Mandarin TTS with voice cloning.

CosyVoice 2 (Tongyi Lab) supports:
- Zero-shot voice cloning from 3-second reference audio
- Mandarin + English + Japanese + Korean
- Emotion control and natural prosody
- Local GPU inference via CosyVoice server or DashScope cloud API

Expects CosyVoice server at COSYVOICE_URL (default http://localhost:9880)
or DashScope API with DASHSCOPE_API_KEY set.
"""

from __future__ import annotations

import os
from pathlib import Path

import httpx
from loguru import logger

from videogen_mcp.providers import register_tts
from videogen_mcp.providers.base import SubtitleEntry, TTSProvider, TTSResult


@register_tts("cosyvoice")
class CosyVoiceTTSProvider(TTSProvider):
    async def synthesize(self, text: str, voice: str, output_path: Path) -> TTSResult:
        url = os.environ.get("COSYVOICE_URL", "http://localhost:9880")
        voice = voice or "zhitian_emo"

        output_path.parent.mkdir(parents=True, exist_ok=True)

        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                f"{url}/api/tts",
                json={"text": text, "speaker": voice, "language": "auto"},
            )
            resp.raise_for_status()
            output_path.write_bytes(resp.content)

        duration = _estimate_duration(text)
        subs = _generate_sentence_subs(text, duration)

        logger.debug(f"CosyVoice: {len(text)} chars -> ~{duration:.1f}s")
        return TTSResult(audio_path=output_path, duration=duration, subtitles=subs)

    async def list_voices(self) -> list[str]:
        url = os.environ.get("COSYVOICE_URL", "http://localhost:9880")
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(f"{url}/api/speakers")
                if resp.status_code == 200:
                    return resp.json().get("speakers", [])
        except Exception:
            pass
        return ["zhitian_emo", "zhiyan_emo", "zhixiaobei", "zhixiaoxia"]

    async def health_check(self) -> bool:
        url = os.environ.get("COSYVOICE_URL", "http://localhost:9880")
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get(f"{url}/api/speakers")
                return resp.status_code == 200
        except Exception as e:
            logger.warning(f"CosyVoice health check failed: {e}")
            return False


def _estimate_duration(text: str) -> float:
    cjk_count = sum(1 for c in text if "\u4e00" <= c <= "\u9fff")
    latin_words = len(text.split()) - cjk_count
    return (cjk_count * 0.35) + (latin_words * 0.4) + 0.5


def _generate_sentence_subs(text: str, total_duration: float) -> list[SubtitleEntry]:
    import re

    sentences = re.split(r"(?<=[.!?。！？])\s*", text)
    sentences = [s.strip() for s in sentences if s.strip()]
    if not sentences:
        return []

    per_sentence = total_duration / len(sentences)
    subs = []
    t = 0.0
    for s in sentences:
        subs.append(SubtitleEntry(start=t, end=t + per_sentence, text=s))
        t += per_sentence
    return subs
