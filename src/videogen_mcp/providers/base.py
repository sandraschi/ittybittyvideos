from __future__ import annotations

import abc
from dataclasses import dataclass
from pathlib import Path


@dataclass
class StockClip:
    url: str
    duration: float
    width: int
    height: int
    source: str


@dataclass
class TTSResult:
    audio_path: Path
    duration: float
    subtitles: list[SubtitleEntry]


@dataclass
class SubtitleEntry:
    start: float
    end: float
    text: str


class LLMProvider(abc.ABC):
    @abc.abstractmethod
    async def generate_script(self, topic: str, paragraph_count: int, language: str = "en") -> dict:
        """Return dict matching VideoScript schema: {title, segments: [{narration, search_terms}]}."""

    @abc.abstractmethod
    async def health_check(self) -> bool: ...


class StockProvider(abc.ABC):
    @abc.abstractmethod
    async def search(self, query: str, count: int = 5, aspect: str = "9:16") -> list[StockClip]:
        """Return stock footage clips matching the query."""

    @abc.abstractmethod
    async def download(self, clip: StockClip, dest: Path) -> Path:
        """Download clip to dest path, return actual path."""

    @abc.abstractmethod
    async def health_check(self) -> bool: ...


class TTSProvider(abc.ABC):
    @abc.abstractmethod
    async def synthesize(self, text: str, voice: str, output_path: Path) -> TTSResult:
        """Generate speech audio + word-level subtitles."""

    @abc.abstractmethod
    async def list_voices(self) -> list[str]: ...

    @abc.abstractmethod
    async def health_check(self) -> bool: ...
