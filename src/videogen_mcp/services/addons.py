"""Addon manager -- optional heavy modules downloaded on demand.

The core installer stays ~60 MB. Heavy ML/DSP deps live in addon packs
that users install from Settings with one click ("The Whole Shebang")
or individually. Downloaded to %LOCALAPPDATA%/ittybitty/addons/{pack}/.

Each addon is a zip containing pre-frozen Python modules (pyd/dll).
At startup, installed addon dirs are added to sys.path so feature
modules can import them transparently.
"""

from __future__ import annotations

import os
import shutil
import sys
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

import httpx
from loguru import logger

ADDON_BASE_URL = "https://github.com/sandraschi/ittybittyvideos/releases/download/addons-v1"

ADDONS_DIR = Path(
    os.environ.get(
        "ITTYBITTY_ADDONS_DIR",
        Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local")) / "ittybitty" / "addons",
    )
)


@dataclass
class AddonInfo:
    id: str
    name: str
    description: str
    size_mb: float
    features: list[str]
    download_url: str
    version: str = "1.0.0"
    installed: bool = False
    install_path: Path = field(default_factory=lambda: Path(""))

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "size_mb": self.size_mb,
            "features": self.features,
            "download_url": self.download_url,
            "version": self.version,
            "installed": self.installed,
            "install_path": str(self.install_path) if self.installed else "",
        }


ADDON_REGISTRY: list[AddonInfo] = [
    AddonInfo(
        id="beat-pack",
        name="Beat Detection",
        description=(
            "Audio-reactive editing. Beat-snap cuts sync footage to music drops."
            " Ducking lowers music under narration."
        ),
        size_mb=120,
        features=["beat-snap cuts", "audio ducking", "BPM detection"],
        download_url=f"{ADDON_BASE_URL}/beat-pack-v1.zip",
    ),
    AddonInfo(
        id="whisper-pack",
        name="Word-Level Subtitles",
        description=(
            "Precision subtitle alignment using AI speech recognition."
            " Enables karaoke-style word highlighting."
        ),
        size_mb=500,
        features=["word-level timing", "karaoke ASS captions", "multi-language alignment"],
        download_url=f"{ADDON_BASE_URL}/whisper-pack-v1.zip",
    ),
    AddonInfo(
        id="vision-pack",
        name="Screening Room",
        description=(
            "AI watches your video and suggests improvements."
            " Flags bad clips, pacing issues, and mismatched footage."
        ),
        size_mb=4000,
        features=["VLM self-critique", "auto clip replacement", "quality scoring"],
        download_url=f"{ADDON_BASE_URL}/vision-pack-v1.zip",
    ),
    AddonInfo(
        id="voice-pack",
        name="Voice Cloning",
        description="Clone any voice from a 3-second sample. Mandarin, English, Japanese, Korean. Local GPU inference.",
        size_mb=2000,
        features=["zero-shot voice cloning", "CosyVoice TTS", "emotion control"],
        download_url=f"{ADDON_BASE_URL}/voice-pack-v1.zip",
    ),
    AddonInfo(
        id="localgen-pack",
        name="AI Video Generation",
        description="Generate video clips from text prompts on your GPU. No API keys, no cloud, no permission needed.",
        size_mb=8000,
        features=["CogVideoX inference", "text-to-video", "6-second clips"],
        download_url=f"{ADDON_BASE_URL}/localgen-pack-v1.zip",
    ),
    AddonInfo(
        id="talker-pack",
        name="Talking Head",
        description="Animate a portrait photo to speak your narration. Picture-in-picture overlay on any video.",
        size_mb=2000,
        features=["face animation", "lip sync", "PiP overlay"],
        download_url=f"{ADDON_BASE_URL}/talker-pack-v1.zip",
    ),
]


def get_addons_dir() -> Path:
    ADDONS_DIR.mkdir(parents=True, exist_ok=True)
    return ADDONS_DIR


def _addon_install_path(addon_id: str) -> Path:
    return get_addons_dir() / addon_id


def is_installed(addon_id: str) -> bool:
    path = _addon_install_path(addon_id)
    return path.exists() and (path / ".addon-manifest.json").exists()


def list_addons() -> list[dict]:
    result = []
    for addon in ADDON_REGISTRY:
        addon.installed = is_installed(addon.id)
        addon.install_path = _addon_install_path(addon.id) if addon.installed else Path("")
        result.append(addon.to_dict())
    return result


def get_addon(addon_id: str) -> AddonInfo | None:
    for addon in ADDON_REGISTRY:
        if addon.id == addon_id:
            addon.installed = is_installed(addon.id)
            return addon
    return None


async def install_addon(addon_id: str, progress_callback=None) -> dict:
    addon = get_addon(addon_id)
    if not addon:
        return {"success": False, "error": f"Unknown addon: {addon_id}"}

    if is_installed(addon_id):
        return {"success": True, "message": f"{addon.name} already installed", "already_installed": True}

    dest = _addon_install_path(addon_id)
    dest.mkdir(parents=True, exist_ok=True)
    zip_path = dest / f"{addon_id}.zip"

    try:
        logger.info(f"Downloading addon {addon.name} ({addon.size_mb} MB)...")
        if progress_callback:
            progress_callback(addon_id, "downloading", 0)

        async with httpx.AsyncClient(follow_redirects=True, timeout=600) as client:
            async with client.stream("GET", addon.download_url) as resp:
                if resp.status_code == 404:
                    _write_placeholder_manifest(dest, addon)
                    return {
                        "success": True,
                        "message": (
                            f"{addon.name} registered"
                            " (addon pack not yet available for download -- coming in v0.3)"
                        ),
                        "placeholder": True,
                    }
                resp.raise_for_status()
                total = int(resp.headers.get("content-length", 0))
                downloaded = 0
                with open(zip_path, "wb") as f:
                    async for chunk in resp.aiter_bytes(chunk_size=65536):
                        f.write(chunk)
                        downloaded += len(chunk)
                        if progress_callback and total:
                            progress_callback(addon_id, "downloading", downloaded / total * 100)

        logger.info(f"Extracting {addon.name}...")
        if progress_callback:
            progress_callback(addon_id, "extracting", 0)

        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(dest)

        zip_path.unlink(missing_ok=True)
        _write_manifest(dest, addon)
        _activate_addon(dest)

        logger.info(f"Addon {addon.name} installed to {dest}")
        return {"success": True, "message": f"{addon.name} installed successfully", "path": str(dest)}

    except Exception as e:
        shutil.rmtree(dest, ignore_errors=True)
        logger.error(f"Addon install failed: {e}")
        return {"success": False, "error": str(e)}


async def install_all(progress_callback=None) -> dict:
    results = {}
    for addon in ADDON_REGISTRY:
        results[addon.id] = await install_addon(addon.id, progress_callback)
    installed = sum(1 for r in results.values() if r.get("success"))
    return {
        "success": True,
        "message": f"Installed {installed}/{len(ADDON_REGISTRY)} addons",
        "results": results,
    }


async def uninstall_addon(addon_id: str) -> dict:
    if not is_installed(addon_id):
        return {"success": False, "error": f"{addon_id} is not installed"}

    dest = _addon_install_path(addon_id)
    shutil.rmtree(dest, ignore_errors=True)
    logger.info(f"Addon {addon_id} uninstalled")
    return {"success": True, "message": f"{addon_id} removed"}


def get_total_size_mb() -> float:
    return sum(a.size_mb for a in ADDON_REGISTRY)


def get_installed_size_mb() -> float:
    return sum(a.size_mb for a in ADDON_REGISTRY if is_installed(a.id))


def activate_installed_addons() -> None:
    for addon in ADDON_REGISTRY:
        path = _addon_install_path(addon.id)
        if path.exists() and (path / ".addon-manifest.json").exists():
            _activate_addon(path)


def _activate_addon(path: Path) -> None:
    path_str = str(path)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)


def _write_manifest(dest: Path, addon: AddonInfo) -> None:
    import json

    manifest = {"id": addon.id, "name": addon.name, "version": addon.version, "features": addon.features}
    (dest / ".addon-manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def _write_placeholder_manifest(dest: Path, addon: AddonInfo) -> None:
    import json

    manifest = {
        "id": addon.id,
        "name": addon.name,
        "version": "placeholder",
        "features": addon.features,
        "note": "Pack not yet available. Will auto-update when released.",
    }
    (dest / ".addon-manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
