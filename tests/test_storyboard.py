from videogen_mcp.models.storyboard import (
    Chapter,
    PlanRequest,
    Scene,
    SceneType,
    ShotType,
    Storyboard,
    TransitionType,
    VideoType,
)


def test_scene_defaults():
    s = Scene(
        scene_type=SceneType.EXPLAINER,
        title="Test",
        narration="Hello world.",
        search_terms=["test"],
    )
    assert s.shot_type == ShotType.MEDIUM
    assert s.duration_target == 10.0
    assert s.transition_out == TransitionType.CUT


def test_chapter_duration():
    ch = Chapter(
        title="Ch1",
        scenes=[
            Scene(scene_type=SceneType.INTRO, title="A", narration="a", search_terms=["a"], duration_target=10),
            Scene(scene_type=SceneType.EXPLAINER, title="B", narration="b", search_terms=["b"], duration_target=20),
        ],
    )
    assert ch.duration == 30.0


def test_storyboard_total_scenes():
    board = Storyboard(
        title="Test",
        video_type=VideoType.TUTORIAL,
        target_duration=120,
        chapters=[
            Chapter(
                title="C1",
                scenes=[
                    Scene(scene_type=SceneType.HOOK, title="H", narration="h", search_terms=["h"]),
                ],
            ),
            Chapter(
                title="C2",
                scenes=[
                    Scene(scene_type=SceneType.EXPLAINER, title="E1", narration="e1", search_terms=["e1"]),
                    Scene(scene_type=SceneType.DEMO, title="D1", narration="d1", search_terms=["d1"]),
                ],
            ),
        ],
    )
    assert board.total_scenes == 3
    assert len(board.all_scenes) == 3


def test_plan_request_defaults():
    req = PlanRequest(topic="Git tutorial")
    assert req.video_type == VideoType.EXPLAINER
    assert req.target_duration == 300.0
    assert req.chapters == 4
    assert req.language == "en"


def test_plan_request_chinese():
    req = PlanRequest(topic="Git 教程", language="zh", chapters=6)
    assert req.language == "zh"
    assert req.chapters == 6


def test_video_type_enum():
    assert VideoType("tutorial") == VideoType.TUTORIAL
    assert VideoType("demo") == VideoType.DEMO
    assert VideoType("documentary") == VideoType.DOCUMENTARY
