from videogen_mcp.models.schema import (
    GenerateRequest,
    JobInfo,
    JobStatus,
    ScriptSegment,
    VideoAspect,
    VideoScript,
)


def test_video_aspect_resolution():
    assert VideoAspect.PORTRAIT.resolution == (1080, 1920)
    assert VideoAspect.LANDSCAPE.resolution == (1920, 1080)
    assert VideoAspect.SQUARE.resolution == (1080, 1080)


def test_generate_request_defaults():
    req = GenerateRequest(topic="cats")
    assert req.topic == "cats"
    assert req.aspect == VideoAspect.PORTRAIT
    assert req.clip_duration == 5.0
    assert req.paragraph_count == 3
    assert req.script is None


def test_generate_request_custom_script():
    req = GenerateRequest(script="Hello world.\n\nSecond paragraph.")
    assert req.script is not None
    assert req.topic == ""


def test_job_info_creation():
    job = JobInfo(topic="dogs")
    assert len(job.job_id) == 12
    assert job.status == JobStatus.PENDING
    assert job.progress == 0.0


def test_job_info_update():
    job = JobInfo(topic="test")
    job.update(JobStatus.SCRIPTING, 25.0)
    assert job.status == JobStatus.SCRIPTING
    assert job.progress == 25.0


def test_video_script_model():
    script = VideoScript(
        title="Test Video",
        segments=[
            ScriptSegment(narration="Hello world.", search_terms=["hello", "world"]),
        ],
    )
    assert len(script.segments) == 1
    assert script.segments[0].narration == "Hello world."


def test_video_aspect_from_string():
    assert VideoAspect("9:16") == VideoAspect.PORTRAIT
    assert VideoAspect("16:9") == VideoAspect.LANDSCAPE
    assert VideoAspect("1:1") == VideoAspect.SQUARE
