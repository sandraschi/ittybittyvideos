from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from loguru import logger

from videogen_mcp.config import get_settings
from videogen_mcp.models.schema import JobInfo, JobStatus

_SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
    job_id TEXT PRIMARY KEY,
    status TEXT NOT NULL,
    progress REAL NOT NULL DEFAULT 0,
    topic TEXT NOT NULL DEFAULT '',
    output_path TEXT NOT NULL DEFAULT '',
    error TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    file_size_bytes INTEGER NOT NULL DEFAULT 0,
    source TEXT NOT NULL DEFAULT 'pipeline'
);
CREATE INDEX IF NOT EXISTS idx_jobs_updated ON jobs(updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
"""


def depot_db_path() -> Path:
    settings = get_settings()
    return settings.videogen_output_dir / "depot.db"


def init_db() -> None:
    path = depot_db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with _connect() as conn:
        conn.executescript(_SCHEMA)


@contextmanager
def _connect():
    conn = sqlite3.connect(depot_db_path(), timeout=30)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def _iso(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat()


def _parse_iso(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _row_to_job(row: sqlite3.Row) -> JobInfo:
    return JobInfo(
        job_id=row["job_id"],
        status=JobStatus(row["status"]),
        progress=float(row["progress"]),
        topic=row["topic"],
        output_path=row["output_path"],
        error=row["error"],
        created_at=_parse_iso(row["created_at"]),
        updated_at=_parse_iso(row["updated_at"]),
    )


def _file_size(path: str) -> int:
    if not path:
        return 0
    p = Path(path)
    return p.stat().st_size if p.is_file() else 0


def upsert_job(job: JobInfo, *, source: str = "pipeline") -> None:
    init_db()
    size = _file_size(job.output_path)
    with _connect() as conn:
        existing = conn.execute("SELECT source FROM jobs WHERE job_id = ?", (job.job_id,)).fetchone()
        src = existing["source"] if existing else source
        conn.execute(
            """
            INSERT INTO jobs (
                job_id, status, progress, topic, output_path, error,
                created_at, updated_at, file_size_bytes, source
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(job_id) DO UPDATE SET
                status = excluded.status,
                progress = excluded.progress,
                topic = excluded.topic,
                output_path = excluded.output_path,
                error = excluded.error,
                updated_at = excluded.updated_at,
                file_size_bytes = excluded.file_size_bytes,
                source = CASE
                    WHEN jobs.source = 'import' AND excluded.source = 'pipeline' THEN 'pipeline'
                    ELSE COALESCE(jobs.source, excluded.source)
                END
            """,
            (
                job.job_id,
                job.status.value,
                job.progress,
                job.topic,
                job.output_path,
                job.error,
                _iso(job.created_at),
                _iso(job.updated_at),
                size,
                src if existing else source,
            ),
        )


def get_job(job_id: str) -> JobInfo | None:
    init_db()
    with _connect() as conn:
        row = conn.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id,)).fetchone()
    return _row_to_job(row) if row else None


def list_jobs(limit: int = 50, *, status: JobStatus | None = None) -> list[JobInfo]:
    init_db()
    with _connect() as conn:
        if status:
            rows = conn.execute(
                "SELECT * FROM jobs WHERE status = ? ORDER BY updated_at DESC LIMIT ?",
                (status.value, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM jobs ORDER BY updated_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
    return [_row_to_job(r) for r in rows]


def list_depot_rows(limit: int = 100) -> list[sqlite3.Row]:
    """Rows with depot metadata for API (complete jobs + on-disk files)."""
    init_db()
    with _connect() as conn:
        return conn.execute(
            """
            SELECT * FROM jobs
            WHERE status = ? OR (output_path != '' AND file_size_bytes > 0)
            ORDER BY updated_at DESC
            LIMIT ?
            """,
            (JobStatus.COMPLETE.value, limit),
        ).fetchall()


def delete_job(job_id: str) -> bool:
    init_db()
    with _connect() as conn:
        cur = conn.execute("DELETE FROM jobs WHERE job_id = ?", (job_id,))
        return cur.rowcount > 0


def scan_output_directory() -> int:
    """Import orphan *.mp4 files in output dir into depot."""
    settings = get_settings()
    output_dir = settings.videogen_output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    imported = 0

    for mp4 in output_dir.glob("*.mp4"):
        job_id = mp4.stem
        if len(job_id) != 12:
            continue
        existing = get_job(job_id)
        if existing:
            updated = existing.model_copy()
            updated.status = JobStatus.COMPLETE
            updated.progress = 100.0
            updated.output_path = str(mp4.resolve())
            updated.updated_at = datetime.fromtimestamp(mp4.stat().st_mtime, tz=timezone.utc)
            upsert_job(updated)
            continue

        mtime = datetime.fromtimestamp(mp4.stat().st_mtime, tz=timezone.utc)
        job = JobInfo(
            job_id=job_id,
            status=JobStatus.COMPLETE,
            progress=100.0,
            topic="Imported render",
            output_path=str(mp4.resolve()),
            created_at=mtime,
            updated_at=mtime,
        )
        upsert_job(job, source="import")
        imported += 1
        logger.info(f"Depot imported orphan video: {mp4.name}")

    return imported


def resolve_output_path(job_id: str) -> Path | None:
    job = get_job(job_id)
    if job and job.output_path:
        p = Path(job.output_path)
        if p.is_file():
            return p
    settings = get_settings()
    candidate = settings.videogen_output_dir / f"{job_id}.mp4"
    return candidate if candidate.is_file() else None
