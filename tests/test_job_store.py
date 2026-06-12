"""Tests for SQLite job depot persistence."""

from pathlib import Path

import pytest

from videogen_mcp.models.schema import JobInfo, JobStatus
from videogen_mcp.services import job_store


@pytest.fixture(autouse=True)
def isolated_depot(tmp_path, monkeypatch):
    out = tmp_path / "output"
    out.mkdir()
    monkeypatch.setenv("VIDEOGEN_OUTPUT_DIR", str(out))
    from videogen_mcp.config.settings import get_settings

    get_settings.cache_clear()
    db = out / "depot.db"
    if db.exists():
        db.unlink()
    yield out


def test_upsert_and_get():
    job = JobInfo(topic="Test topic")
    job_store.upsert_job(job)
    loaded = job_store.get_job(job.job_id)
    assert loaded is not None
    assert loaded.topic == "Test topic"
    assert loaded.status == JobStatus.PENDING


def test_list_jobs_order():
    a = JobInfo(topic="A")
    b = JobInfo(topic="B")
    job_store.upsert_job(a)
    job_store.upsert_job(b)
    jobs = job_store.list_jobs(10)
    assert len(jobs) >= 2
    assert jobs[0].job_id == b.job_id


def test_scan_imports_orphan_mp4(isolated_depot: Path):
    job_id = "aabbccddeeff"
    mp4 = isolated_depot / f"{job_id}.mp4"
    mp4.write_bytes(b"\x00" * 128)
    imported = job_store.scan_output_directory()
    assert imported == 1
    job = job_store.get_job(job_id)
    assert job is not None
    assert job.status == JobStatus.COMPLETE
    assert job.topic == "Imported render"


def test_resolve_output_path(isolated_depot: Path):
    job_id = "112233445566"
    mp4 = isolated_depot / f"{job_id}.mp4"
    mp4.write_bytes(b"\x00" * 64)
    assert job_store.resolve_output_path(job_id) == mp4


def test_delete_job(isolated_depot: Path):
    job = JobInfo(topic="delete me")
    job_store.upsert_job(job)
    assert job_store.delete_job(job.job_id) is True
    assert job_store.get_job(job.job_id) is None


def test_scan_updates_existing_job(isolated_depot: Path):
    job_id = "998877665544"
    job = JobInfo(job_id=job_id, topic="Dog video", status=JobStatus.COMPLETE, progress=100.0)
    job_store.upsert_job(job)
    mp4 = isolated_depot / f"{job_id}.mp4"
    mp4.write_bytes(b"\x00" * 256)
    job_store.scan_output_directory()
    loaded = job_store.get_job(job_id)
    assert loaded.output_path == str(mp4.resolve())


def test_depot_list_and_summary(isolated_depot: Path):
    from videogen_mcp.services.depot import depot_summary, list_depot

    job_id = "deadbeefcafe"
    mp4 = isolated_depot / f"{job_id}.mp4"
    mp4.write_bytes(b"\x00" * 512)
    job_store.scan_output_directory()
    items = list_depot(10)
    assert any(i.job_id == job_id for i in items)
    summary = depot_summary()
    assert summary.on_disk >= 1
    assert str(isolated_depot) in summary.output_dir
