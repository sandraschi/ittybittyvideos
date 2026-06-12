"""Social publish helpers — minimum-fuss handoff to TikTok, Shorts, Reels, etc."""

from __future__ import annotations

import re
from typing import Any

from videogen_mcp.models.schema import JobInfo, JobStatus

PLATFORMS: list[dict[str, Any]] = [
    {
        "id": "tiktok",
        "label": "TikTok",
        "upload_url": "https://www.tiktok.com/upload",
        "creator_url": "https://www.tiktok.com/tiktokstudio/upload",
        "aspect": "9:16",
        "max_short_s": 180,
        "api_tier": "manual",
        "notes": "Desktop upload or TikTok Studio. API requires app review.",
    },
    {
        "id": "youtube_shorts",
        "label": "YouTube Shorts",
        "upload_url": "https://studio.youtube.com/",
        "creator_url": "https://www.youtube.com/upload",
        "aspect": "9:16",
        "max_short_s": 180,
        "api_tier": "api_optional",
        "notes": "Vertical ≤3 min counts as Shorts. YouTube Data API resumable upload (future env).",
    },
    {
        "id": "instagram_reels",
        "label": "Instagram Reels",
        "upload_url": "https://www.instagram.com/",
        "creator_url": "https://business.facebook.com/creatorstudio",
        "aspect": "9:16",
        "max_short_s": 90,
        "api_tier": "manual",
        "notes": "Phone upload or Meta Business Suite / Creator Studio on desktop.",
    },
    {
        "id": "douyin",
        "label": "Douyin",
        "upload_url": "https://creator.douyin.com/creator-micro/content/upload",
        "creator_url": "https://creator.douyin.com/",
        "aspect": "9:16",
        "max_short_s": 600,
        "api_tier": "manual",
        "notes": "Creator platform; use CosyVoice stack for CN narration.",
    },
    {
        "id": "linkedin",
        "label": "LinkedIn",
        "upload_url": "https://www.linkedin.com/feed/",
        "creator_url": "https://www.linkedin.com/feed/",
        "aspect": "16:9",
        "max_short_s": 600,
        "api_tier": "manual",
        "notes": "Start a post → Add video. Better for 16:9 explainers.",
    },
]


def _slug_words(text: str, limit: int = 4) -> list[str]:
    words = re.findall(r"[a-zA-Z0-9\u4e00-\u9fff]+", text.lower())
    return words[:limit]


def _hashtags(topic: str) -> list[str]:
    base = ["#roughcutvideos", "#ai", "#explainer"]
    for w in _slug_words(topic, 3):
        if len(w) > 2:
            base.append(f"#{w}")
    platform_tags = {
        "tiktok": ["#fyp", "#learnontiktok"],
        "douyin": ["#抖音", "#知识分享"],
    }
    return list(dict.fromkeys(base + platform_tags.get("tiktok", [])))[:8]


def build_publish_pack(job: JobInfo) -> dict[str, Any]:
    """Caption, hashtags, platform links, and download path for a completed job."""
    title = (job.topic or "Untitled").strip()[:100]
    hashtags = _hashtags(title)
    tag_line = " ".join(hashtags)
    caption = f"{title}\n\n{tag_line}"

    ready = job.status == JobStatus.COMPLETE and bool(job.output_path)
    download_url = f"/api/v1/jobs/{job.job_id}/download" if ready else ""

    recommended = [p for p in PLATFORMS if p["id"] in ("tiktok", "youtube_shorts", "douyin", "instagram_reels")]

    return {
        "success": True,
        "job_id": job.job_id,
        "ready": ready,
        "title": title,
        "caption": caption,
        "hashtags": hashtags,
        "output_path": job.output_path if ready else "",
        "download_url": download_url,
        "platforms": PLATFORMS,
        "recommended_platforms": recommended,
        "workflow": [
            "Download MP4 (or Reveal in Explorer on Windows).",
            "Copy caption + hashtags.",
            "Open platform upload page in a new tab.",
            "Upload file, paste caption, publish.",
        ],
        "future_api": {
            "youtube": "Set YOUTUBE_CLIENT_SECRETS + OAuth for resumable Shorts upload (v0.2).",
            "tiktok": "TikTok Content Posting API — app review required.",
            "postiz": "Self-hosted Postiz/Buffer for schedule-once-publish-many.",
        },
    }
