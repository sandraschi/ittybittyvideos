"""Agentic storyboard planner -- LLM generates multi-scene video structure.

For intermediate-length videos (3-10 min), the planner:
1. Takes topic + video_type + target_duration
2. LLM generates a chaptered storyboard with scene-level detail
3. Videographer rules post-process for pacing/B-roll/transitions
4. Returns a Storyboard ready for scene-by-scene pipeline execution
"""

from __future__ import annotations

import json
import re

from loguru import logger

from videogen_mcp.models.storyboard import (
    Chapter,
    PlanRequest,
    Scene,
    SceneType,
    ShotType,
    Storyboard,
    TransitionType,
)
from videogen_mcp.services.videographer import apply_videographer_rules

PLANNER_SYSTEM = """You are a professional video storyboard planner. Given a topic, video type,
target duration, and chapter count, produce a JSON storyboard.

Return ONLY valid JSON with this structure:
{
  "title": "Video title",
  "chapters": [
    {
      "title": "Chapter title",
      "scenes": [
        {
          "scene_type": "hook|intro|explainer|demo|broll|recap|outro",
          "title": "Scene label",
          "narration": "What the narrator says (2-4 sentences, natural speech)",
          "search_terms": ["keyword1", "keyword2", "keyword3"],
          "shot_type": "wide|medium|close|screen_capture|text_overlay|aerial",
          "duration_target": 15.0,
          "notes": "optional director notes"
        }
      ]
    }
  ]
}

Rules:
- First scene should be a "hook" (3-5 seconds, attention-grabbing statement)
- Last scene should be an "outro"
- Mix scene types: explainer for concepts, demo for showing things, broll for visual breaks
- Vary shot types for visual interest
- Each narration segment should be spoken naturally, no markdown, no labels
- Search terms should find relevant stock footage or AI-generated video
- Duration targets should sum to approximately the requested total duration
- For tutorials/demos: include "screen_capture" shot types for UI walkthroughs
- For documentaries: favor "wide" and "aerial" shots with longer scenes
- Match narration language to the requested language"""


async def plan_video(request: PlanRequest) -> Storyboard:
    prompt = (
        f"Topic: {request.topic}\n"
        f"Video type: {request.video_type.value}\n"
        f"Target duration: {request.target_duration} seconds ({request.target_duration / 60:.1f} minutes)\n"
        f"Chapters: {request.chapters}\n"
        f"Language: {request.language}\n"
    )
    if request.style_notes:
        prompt += f"Style notes: {request.style_notes}\n"

    from openai import AsyncOpenAI

    from videogen_mcp.config import get_settings

    settings = get_settings()
    client = AsyncOpenAI(api_key=settings.openai_api_key, base_url=settings.openai_base_url)
    resp = await client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": PLANNER_SYSTEM},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=4000,
    )
    raw = resp.choices[0].message.content or ""
    raw = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL).strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    data = json.loads(raw)

    chapters = []
    for ch_data in data.get("chapters", []):
        scenes = []
        for s_data in ch_data.get("scenes", []):
            scenes.append(
                Scene(
                    scene_type=SceneType(s_data.get("scene_type", "explainer")),
                    title=s_data.get("title", ""),
                    narration=s_data.get("narration", ""),
                    search_terms=s_data.get("search_terms", []),
                    shot_type=ShotType(s_data.get("shot_type", "medium")),
                    duration_target=float(s_data.get("duration_target", 10.0)),
                    transition_out=TransitionType(s_data.get("transition_out", "cut")),
                    notes=s_data.get("notes", ""),
                )
            )
        chapters.append(Chapter(title=ch_data.get("title", ""), scenes=scenes))

    board = Storyboard(
        title=data.get("title", request.topic),
        video_type=request.video_type,
        target_duration=request.target_duration,
        chapters=chapters,
        language=request.language,
    )

    board = apply_videographer_rules(board)
    logger.info(
        f"Planned: '{board.title}' -- {board.total_scenes} scenes, "
        f"{len(board.chapters)} chapters, {board.planned_duration:.0f}s"
    )
    return board
