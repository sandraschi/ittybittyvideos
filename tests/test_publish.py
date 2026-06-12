from videogen_mcp.models.schema import JobInfo, JobStatus
from videogen_mcp.services.publish import PLATFORMS, build_publish_pack


def test_platforms_not_empty():
    assert len(PLATFORMS) >= 4
    ids = {p["id"] for p in PLATFORMS}
    assert "tiktok" in ids
    assert "youtube_shorts" in ids


def test_publish_pack_incomplete_job():
    job = JobInfo(topic="Quantum cats", status=JobStatus.COMPOSING, progress=50.0)
    pack = build_publish_pack(job)
    assert pack["ready"] is False
    assert pack["download_url"] == ""
    assert "Quantum cats" in pack["caption"]


def test_publish_pack_complete_job():
    job = JobInfo(
        topic="Test topic",
        status=JobStatus.COMPLETE,
        output_path="output/abc123.mp4",
    )
    pack = build_publish_pack(job)
    assert pack["ready"] is True
    assert pack["download_url"].endswith("/download")
    assert len(pack["hashtags"]) >= 3
    assert pack["platforms"][0]["upload_url"].startswith("http")
