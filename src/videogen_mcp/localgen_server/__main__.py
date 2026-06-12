"""Run local Wan 2.2 / LocalGen HTTP sidecar (port 8188 by default)."""

from __future__ import annotations

import os


def main() -> None:
    import uvicorn

    host = os.environ.get("LOCALGEN_HOST", os.environ.get("COGVIDEO_HOST", "127.0.0.1"))
    port = int(os.environ.get("LOCALGEN_PORT", os.environ.get("COGVIDEO_PORT", "8188")))
    uvicorn.run(
        "videogen_mcp.localgen_server.app:app",
        host=host,
        port=port,
        log_level=os.environ.get("LOCALGEN_LOG_LEVEL", "info"),
    )


if __name__ == "__main__":
    main()
