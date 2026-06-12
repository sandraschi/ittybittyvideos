from __future__ import annotations

import subprocess
from pathlib import Path

from pydantic import BaseModel, Field

from videogen_mcp.config import get_settings
from videogen_mcp.models.schema import JobStatus
from videogen_mcp.services import job_store


class DepotItem(BaseModel):
    job_id: str
    topic: str
    status: str
    progress: float = 100.0
    output_path: str = ""
    file_size_bytes: int = 0
    file_size_mb: float = 0.0
    created_at: str
    updated_at: str
    source: str = "pipeline"
    has_file: bool = False
    download_url: str = ""
    publish_url: str = ""
    poster_url: str = ""
    error: str = ""


class DepotSummary(BaseModel):
    output_dir: str
    db_path: str
    total: int
    on_disk: int
    imported: int = 0


def _row_item(row) -> DepotItem:
    path = row["output_path"] or ""
    has_file = bool(path and Path(path).is_file())
    if not has_file:
        resolved = job_store.resolve_output_path(row["job_id"])
        has_file = resolved is not None
        if resolved:
            path = str(resolved)
    size = row["file_size_bytes"] or (Path(path).stat().st_size if has_file else 0)
    jid = row["job_id"]
    return DepotItem(
        job_id=jid,
        topic=row["topic"] or "Untitled",
        status=row["status"],
        progress=float(row["progress"]),
        output_path=path,
        file_size_bytes=size,
        file_size_mb=round(size / 1024 / 1024, 2) if size else 0.0,
        created_at=row["created_at"],
        updated_at=row["updated_at"],
        source=row["source"],
        has_file=has_file,
        download_url=f"/api/v1/jobs/{jid}/download" if has_file else "",
        publish_url=f"/publish?job={jid}",
        poster_url=f"/api/v1/depot/{jid}/poster" if has_file else "",
        error=row["error"] or "",
    )


def list_depot(limit: int = 100) -> list[DepotItem]:
    rows = job_store.list_depot_rows(limit)
    items = [_row_item(r) for r in rows]
    return [i for i in items if i.has_file or i.status in (JobStatus.COMPLETE.value, JobStatus.FAILED.value)]


def depot_summary() -> DepotSummary:
    settings = get_settings()
    items = list_depot(500)
    on_disk = sum(1 for i in items if i.has_file)
    imported = sum(1 for i in items if i.source == "import")
    return DepotSummary(
        output_dir=str(settings.videogen_output_dir.resolve()),
        db_path=str(job_store.depot_db_path().resolve()),
        total=len(items),
        on_disk=on_disk,
        imported=imported,
    )


def scan_depot() -> DepotSummary:
    imported = job_store.scan_output_directory()
    summary = depot_summary()
    summary.imported = imported
    return summary


def delete_depot_item(job_id: str, *, delete_file: bool = True) -> bool:
    path = job_store.resolve_output_path(job_id)
    if delete_file and path and path.is_file():
        path.unlink(missing_ok=True)
    work = get_settings().videogen_output_dir / job_id
    if delete_file and work.is_dir():
        for f in work.iterdir():
            f.unlink(missing_ok=True)
        work.rmdir()
    poster = poster_path(job_id)
    if delete_file and poster and poster.is_file():
        poster.unlink(missing_ok=True)
    return job_store.delete_job(job_id)


def poster_path(job_id: str) -> Path | None:
    settings = get_settings()
    return settings.videogen_output_dir / job_id / "poster.jpg"


def ensure_poster(job_id: str) -> Path | None:
    import shutil

    out = poster_path(job_id)
    if out and out.is_file():
        return out
    mp4 = job_store.resolve_output_path(job_id)
    if not mp4:
        return None
    out.parent.mkdir(parents=True, exist_ok=True)
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        return None
    result = subprocess.run(
        [
            ffmpeg,
            "-y",
            "-ss",
            "1",
            "-i",
            str(mp4),
            "-vframes",
            "1",
            "-q:v",
            "3",
            str(out),
        ],
        capture_output=True,
        timeout=60,
    )
    return out if result.returncode == 0 and out.is_file() else None
