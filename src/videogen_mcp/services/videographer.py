"""Videographer rules engine -- codified professional video editing patterns.

Applies post-processing to LLM-generated storyboards to enforce pacing,
B-roll distribution, hook structure, and transition coherence. These rules
come from documentary/tutorial editing conventions, not LLM hallucination.
"""

from __future__ import annotations

from loguru import logger

from videogen_mcp.models.storyboard import (
    Scene,
    SceneType,
    ShotType,
    Storyboard,
    TransitionType,
    VideoType,
)

PACING_RULES = {
    VideoType.TUTORIAL: {"min_scene": 5.0, "max_scene": 30.0, "broll_ratio": 0.2},
    VideoType.DEMO: {"min_scene": 3.0, "max_scene": 20.0, "broll_ratio": 0.15},
    VideoType.EXPLAINER: {"min_scene": 4.0, "max_scene": 25.0, "broll_ratio": 0.25},
    VideoType.DOCUMENTARY: {"min_scene": 6.0, "max_scene": 40.0, "broll_ratio": 0.3},
    VideoType.SHOWCASE: {"min_scene": 3.0, "max_scene": 15.0, "broll_ratio": 0.2},
}


def apply_videographer_rules(board: Storyboard) -> Storyboard:
    board = _enforce_hook(board)
    board = _enforce_outro(board)
    board = _enforce_pacing(board)
    board = _insert_broll(board)
    board = _enforce_transitions(board)
    board = _rebalance_duration(board)
    logger.debug(f"Videographer: {board.total_scenes} scenes, {board.planned_duration:.0f}s planned")
    return board


def _enforce_hook(board: Storyboard) -> Storyboard:
    if not board.chapters or not board.chapters[0].scenes:
        return board

    first = board.chapters[0].scenes[0]
    if first.scene_type != SceneType.HOOK:
        hook = Scene(
            scene_type=SceneType.HOOK,
            title="Hook",
            narration=first.narration.split(".")[0] + ".",
            search_terms=first.search_terms[:2],
            shot_type=ShotType.CLOSE,
            duration_target=min(5.0, board.target_duration * 0.02),
            transition_out=TransitionType.CUT,
            notes="Grab attention in first 3 seconds",
        )
        board.chapters[0].scenes.insert(0, hook)
    return board


def _enforce_outro(board: Storyboard) -> Storyboard:
    if not board.chapters:
        return board

    last_chapter = board.chapters[-1]
    if not last_chapter.scenes or last_chapter.scenes[-1].scene_type != SceneType.OUTRO:
        outro = Scene(
            scene_type=SceneType.OUTRO,
            title="Outro",
            narration="Thanks for watching.",
            search_terms=["conclusion", "summary"],
            shot_type=ShotType.WIDE,
            duration_target=min(8.0, board.target_duration * 0.03),
            transition_out=TransitionType.FADE_BLACK,
        )
        last_chapter.scenes.append(outro)
    return board


def _enforce_pacing(board: Storyboard) -> Storyboard:
    rules = PACING_RULES.get(board.video_type, PACING_RULES[VideoType.EXPLAINER])
    for scene in board.all_scenes:
        if scene.scene_type == SceneType.HOOK:
            scene.duration_target = min(scene.duration_target, 5.0)
        elif scene.scene_type == SceneType.OUTRO:
            scene.duration_target = min(scene.duration_target, 10.0)
        else:
            scene.duration_target = max(rules["min_scene"], min(rules["max_scene"], scene.duration_target))
    return board


def _insert_broll(board: Storyboard) -> Storyboard:
    for chapter in board.chapters:
        consecutive_aroll = 0
        insert_indices: list[int] = []

        for i, scene in enumerate(chapter.scenes):
            if scene.scene_type == SceneType.BROLL:
                consecutive_aroll = 0
            else:
                consecutive_aroll += 1
                if consecutive_aroll >= 3:
                    insert_indices.append(i)
                    consecutive_aroll = 0

        for offset, idx in enumerate(insert_indices):
            prev_scene = chapter.scenes[idx + offset]
            broll = Scene(
                scene_type=SceneType.BROLL,
                title=f"B-roll: {prev_scene.title}",
                narration="",
                search_terms=prev_scene.search_terms[:2] + ["cinematic"],
                shot_type=ShotType.WIDE,
                duration_target=4.0,
                transition_out=TransitionType.CROSSFADE,
                notes="Visual breathing room",
            )
            chapter.scenes.insert(idx + offset + 1, broll)
    return board


def _enforce_transitions(board: Storyboard) -> Storyboard:
    all_scenes = board.all_scenes
    for i, scene in enumerate(all_scenes):
        if scene.scene_type == SceneType.HOOK:
            scene.transition_out = TransitionType.CUT
        elif scene.scene_type == SceneType.OUTRO:
            scene.transition_out = TransitionType.FADE_BLACK
        elif scene.scene_type == SceneType.BROLL:
            scene.transition_out = TransitionType.CROSSFADE
        elif i > 0 and all_scenes[i - 1].scene_type == SceneType.BROLL:
            pass
        elif i < len(all_scenes) - 1:
            next_scene = all_scenes[i + 1]
            if next_scene.scene_type != scene.scene_type:
                scene.transition_out = TransitionType.CROSSFADE
            else:
                scene.transition_out = TransitionType.CUT
    return board


def _rebalance_duration(board: Storyboard) -> Storyboard:
    if board.planned_duration <= 0:
        return board

    ratio = board.target_duration / board.planned_duration
    if 0.8 <= ratio <= 1.2:
        return board

    for scene in board.all_scenes:
        if scene.scene_type not in (SceneType.HOOK, SceneType.OUTRO):
            scene.duration_target = round(scene.duration_target * ratio, 1)
    return board
