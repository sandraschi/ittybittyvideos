from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from videogen_mcp.localgen_server.app import app


@pytest.fixture
def gen_client():
    return TestClient(app)


def test_localgen_health(gen_client):
    resp = gen_client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["service"] == "localgen-server"
    assert data["tier"] in ("2026", "2026-fast", "legacy")
    assert "wan22" in data["backend"] or data["backend"] == "cogvideo-2b"


def test_localgen_generate_missing_deps(gen_client):
    with patch("videogen_mcp.localgen_server.pipeline.get_runtime_info") as mock_info:
        from videogen_mcp.localgen_server.pipeline import RuntimeInfo

        mock_info.return_value = RuntimeInfo(
            backend="wan22-14b",
            model_id="Wan-AI/Wan2.2-T2V-A14B-Diffusers",
            label="Wan 2.2 T2V 14B",
            tier="2026",
            device="cuda",
            cuda_available=False,
            deps_installed=False,
        )
        resp = gen_client.post(
            "/api/generate",
            json={"prompt": "a dog running on a beach", "aspect": "9:16"},
        )
    assert resp.status_code == 503


def test_localgen_generate_success(gen_client):
    fake_mp4 = b"\x00\x00\x00\x18ftypmp42" + b"\x00" * 64

    async def fake_gen(*args, **kwargs):
        return fake_mp4

    with patch("videogen_mcp.localgen_server.pipeline.get_runtime_info") as mock_info:
        from videogen_mcp.localgen_server.pipeline import RuntimeInfo

        mock_info.return_value = RuntimeInfo(
            backend="wan22-14b",
            model_id="Wan-AI/Wan2.2-T2V-A14B-Diffusers",
            label="Wan 2.2 T2V 14B",
            tier="2026",
            device="cuda",
            cuda_available=True,
            deps_installed=True,
        )
        with patch("videogen_mcp.localgen_server.pipeline.generate_video_bytes", fake_gen):
            resp = gen_client.post(
                "/api/generate",
                json={"prompt": "sunset over mountains", "num_frames": 81},
            )
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "video/mp4"
    assert resp.content.startswith(b"\x00\x00\x00\x18ftyp")
