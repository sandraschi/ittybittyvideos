from videogen_mcp.models.storyboard import (
    Chapter,
    Scene,
    SceneType,
    Storyboard,
    TransitionType,
    VideoType,
)
from videogen_mcp.services.videographer import (
    _enforce_hook,
    _enforce_outro,
    _enforce_pacing,
    _enforce_transitions,
    _insert_broll,
    _rebalance_duration,
    apply_videographer_rules,
)


def _make_board(scenes: list[Scene], target: float = 120.0) -> Storyboard:
    return Storyboard(
        title="Test",
        video_type=VideoType.EXPLAINER,
        target_duration=target,
        chapters=[Chapter(title="Ch1", scenes=scenes)],
    )


def test_enforce_hook_adds_hook():
    board = _make_board(
        [
            Scene(scene_type=SceneType.INTRO, title="Intro", narration="Welcome to the show.", search_terms=["intro"]),
        ]
    )
    board = _enforce_hook(board)
    assert board.chapters[0].scenes[0].scene_type == SceneType.HOOK


def test_enforce_hook_preserves_existing():
    board = _make_board(
        [
            Scene(scene_type=SceneType.HOOK, title="Hook", narration="Boom.", search_terms=["boom"]),
            Scene(scene_type=SceneType.INTRO, title="Intro", narration="Welcome.", search_terms=["intro"]),
        ]
    )
    board = _enforce_hook(board)
    assert len(board.chapters[0].scenes) == 2


def test_enforce_outro_adds_outro():
    board = _make_board(
        [
            Scene(scene_type=SceneType.EXPLAINER, title="Explain", narration="Stuff.", search_terms=["stuff"]),
        ]
    )
    board = _enforce_outro(board)
    assert board.chapters[-1].scenes[-1].scene_type == SceneType.OUTRO


def test_insert_broll_after_3_consecutive():
    scenes = [
        Scene(scene_type=SceneType.EXPLAINER, title=f"S{i}", narration=f"n{i}", search_terms=[f"s{i}"])
        for i in range(5)
    ]
    board = _make_board(scenes)
    board = _insert_broll(board)
    types = [s.scene_type for s in board.chapters[0].scenes]
    assert SceneType.BROLL in types


def test_enforce_pacing_clamps():
    board = _make_board(
        [
            Scene(scene_type=SceneType.EXPLAINER, title="S", narration="n", search_terms=["s"], duration_target=100),
        ]
    )
    board = _enforce_pacing(board)
    assert board.chapters[0].scenes[0].duration_target <= 25.0


def test_enforce_transitions_outro_fades():
    board = _make_board(
        [
            Scene(scene_type=SceneType.EXPLAINER, title="E", narration="n", search_terms=["e"]),
            Scene(scene_type=SceneType.OUTRO, title="O", narration="bye", search_terms=["bye"]),
        ]
    )
    board = _enforce_transitions(board)
    assert board.chapters[0].scenes[-1].transition_out == TransitionType.FADE_BLACK


def test_rebalance_stretches():
    board = _make_board(
        [Scene(scene_type=SceneType.EXPLAINER, title="S", narration="n", search_terms=["s"], duration_target=10)],
        target=50.0,
    )
    board = _rebalance_duration(board)
    assert board.chapters[0].scenes[0].duration_target > 10.0


def test_full_rules_pipeline():
    scenes = [
        Scene(scene_type=SceneType.INTRO, title="Intro", narration="Welcome.", search_terms=["welcome"]),
        Scene(scene_type=SceneType.EXPLAINER, title="E1", narration="Part one.", search_terms=["part1"]),
        Scene(scene_type=SceneType.EXPLAINER, title="E2", narration="Part two.", search_terms=["part2"]),
        Scene(scene_type=SceneType.EXPLAINER, title="E3", narration="Part three.", search_terms=["part3"]),
        Scene(scene_type=SceneType.RECAP, title="Recap", narration="Summary.", search_terms=["summary"]),
    ]
    board = _make_board(scenes, target=120.0)
    board = apply_videographer_rules(board)
    all_types = [s.scene_type for s in board.all_scenes]
    assert all_types[0] == SceneType.HOOK
    assert all_types[-1] == SceneType.OUTRO
    assert SceneType.BROLL in all_types
