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
from videogen_mcp.services.prompt_director import enrich_for_planner
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


def _planner_endpoint(settings) -> tuple[str, str, str]:
    """Resolve (api_key, base_url, model) from the configured LLM provider.

    The planner needs raw chat completions (storyboard JSON), not the
    LLMProvider.generate_script interface, so it routes by provider name
    to the matching OpenAI-compatible endpoint instead of hardcoding OpenAI."""
    p = settings.videogen_llm_provider
    if p == "deepseek":
        return settings.deepseek_api_key, settings.deepseek_base_url, settings.deepseek_model
    if p == "lmstudio":
        return settings.lmstudio_api_key, settings.lmstudio_base_url, settings.lmstudio_model
    if p == "ollama":
        return "ollama", settings.ollama_base_url, settings.ollama_model
    return settings.openai_api_key, settings.openai_base_url, settings.openai_model


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
    hint = request.visual_look().planner_hint()
    if hint:
        prompt += f"{hint}\n"

    system_content, user_content = enrich_for_planner(
        PLANNER_SYSTEM, prompt, request.structure, request.style_notes, request.intro
    )

    from openai import AsyncOpenAI

    from videogen_mcp.config import get_settings

    settings = get_settings()
    api_key, base_url, model = _planner_endpoint(settings)
    logger.debug(f"planner: using {settings.videogen_llm_provider} ({base_url}, {model})")
    client = AsyncOpenAI(api_key=api_key, base_url=base_url)
    resp = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content},
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
