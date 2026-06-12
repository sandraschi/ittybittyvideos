from __future__ import annotations

from pathlib import Path

import edge_tts
from loguru import logger

from videogen_mcp.config import get_settings
from videogen_mcp.providers import register_tts
from videogen_mcp.providers.base import SubtitleEntry, TTSProvider, TTSResult


@register_tts("edge-tts")
class EdgeTTSProvider(TTSProvider):
    async def synthesize(self, text: str, voice: str, output_path: Path) -> TTSResult:
        if not voice:
            voice = get_settings().edge_tts_voice

        output_path.parent.mkdir(parents=True, exist_ok=True)
        communicate = edge_tts.Communicate(text, voice)

        subs: list[SubtitleEntry] = []
        with open(output_path, "wb") as f:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    f.write(chunk["data"])
                elif chunk["type"] == "WordBoundary":
                    offset_ms = chunk["offset"] / 10_000
                    duration_ms = chunk["duration"] / 10_000
                    subs.append(
                        SubtitleEntry(
                            start=offset_ms / 1000,
                            end=(offset_ms + duration_ms) / 1000,
                            text=chunk["text"],
                        )
                    )

        duration = subs[-1].end if subs else 0.0
        sentence_subs = _merge_word_to_sentence(subs, text)

        logger.debug(f"TTS: {len(text)} chars -> {duration:.1f}s audio, {len(sentence_subs)} subtitle entries")
        return TTSResult(audio_path=output_path, duration=duration, subtitles=sentence_subs, words=subs or None)

    async def list_voices(self) -> list[str]:
        voices = await edge_tts.list_voices()
        return [v["ShortName"] for v in voices]

    async def health_check(self) -> bool:
        try:
            voices = await edge_tts.list_voices()
            return len(voices) > 0
        except Exception as e:
            logger.warning(f"Edge TTS health check failed: {e}")
            return False


def _merge_word_to_sentence(words: list[SubtitleEntry], full_text: str) -> list[SubtitleEntry]:
    if not words:
        return []

    sentences: list[SubtitleEntry] = []
    current_words: list[SubtitleEntry] = []

    for w in words:
        current_words.append(w)
        if w.text.rstrip().endswith((".", "!", "?", "。", "！", "？")):
            sentences.append(
                SubtitleEntry(
                    start=current_words[0].start,
                    end=current_words[-1].end,
                    text=" ".join(cw.text for cw in current_words),
                )
            )
            current_words = []

    if current_words:
        sentences.append(
            SubtitleEntry(
                start=current_words[0].start,
                end=current_words[-1].end,
                text=" ".join(cw.text for cw in current_words),
            )
        )

    return sentences
