from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from videogen_mcp.localgen_server.app import app
from videogen_mcp.localgen_server.backends import BACKENDS
from videogen_mcp.localgen_server.backends.loader import backend_meta, resolve_backend_key


@pytest.fixture
def gen_client():
    return TestClient(app)


def test_longcat_backend_registry():
    assert "longcat-video-13b" in BACKENDS
    meta = BACKENDS["longcat-video-13b"]
    assert meta["model_id"] == "meituan-longcat/LongCat-Video"
    assert meta["fps"] == "30"
    assert meta["tier"] == "2026"


def test_resolve_longcat_backend():
    with patch.dict("os.environ", {"LOCALGEN_BACKEND": "longcat-video-13b"}):
        key = resolve_backend_key()
        assert key == "longcat-video-13b"
        meta = backend_meta(key)
        assert meta["model_id"] == "meituan-longcat/LongCat-Video"


def test_localgen_extend_endpoint(gen_client):
    fake_mp4 = b"\x00\x00\x00\x18ftypmp42" + b"\x00" * 64

    async def fake_gen(*args, **kwargs):
        return fake_mp4

    with patch("videogen_mcp.localgen_server.pipeline.get_runtime_info") as mock_info:
        from videogen_mcp.localgen_server.pipeline import RuntimeInfo

        mock_info.return_value = RuntimeInfo(
            backend="longcat-video-13b",
            model_id="meituan-longcat/LongCat-Video",
            label="LongCat-Video 13.6B (DiT Video Continuation)",
            tier="2026",
            device="cuda",
            cuda_available=True,
            deps_installed=True,
        )
        with patch("videogen_mcp.localgen_server.pipeline.generate_video_bytes", fake_gen):
            resp = gen_client.post(
                "/api/extend",
                json={"prompt": "extend sunset view over ocean", "num_frames": 81},
            )
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "video/mp4"
    assert resp.content.startswith(b"\x00\x00\x00\x18ftyp")
