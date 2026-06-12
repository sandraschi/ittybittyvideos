import os

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("VIDEOGEN_LLM_PROVIDER", "openai")
os.environ.setdefault("VIDEOGEN_STOCK_PROVIDER", "pexels")
os.environ.setdefault("VIDEOGEN_TTS_PROVIDER", "edge-tts")
os.environ.setdefault("VIDEOGEN_OUTPUT_DIR", "./test_output")
os.environ.setdefault("VIDEOGEN_CACHE_DIR", "./test_cache")


@pytest.fixture
def client():
    from videogen_mcp.server import rest

    return TestClient(rest)
