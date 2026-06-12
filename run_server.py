"""Entry point for PyInstaller-bundled server."""
import _strptime  # noqa: F401 — PyInstaller must bundle this eagerly
import sys

sys.path.insert(0, ".")

from videogen_mcp.server import main

main()
