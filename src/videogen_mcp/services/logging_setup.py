"""Wire loguru + key events into the activity log ring buffer."""

from __future__ import annotations

from loguru import logger

from videogen_mcp.services.activity_log import log_activity

_sink_installed = False


def _loguru_sink(message) -> None:
    record = message.record
    level = record["level"].name
    if level == "WARN":
        level = "WARNING"
    log_activity(
        kind="server",
        detail=str(record["message"]),
        level=level,
        meta={"logger": record["name"], "module": record["module"]},
    )


def install_activity_logging() -> None:
    global _sink_installed
    if _sink_installed:
        return
    logger.add(_loguru_sink, level="DEBUG", format="{message}")
    _sink_installed = True
    log_activity("system", "roughcutvideos activity log ready", level="INFO")


def log_api(kind: str, detail: str, *, level: str = "INFO", **meta) -> None:
    log_activity(kind, detail, level=level, meta=meta or None)
