import pytest
from fastapi.testclient import TestClient

from videogen_mcp.server import rest


@pytest.fixture
def client():
    return TestClient(rest)


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["service"] == "videogen-mcp"


def test_list_jobs_empty(client):
    resp = client.get("/api/v1/jobs")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert isinstance(data["jobs"], list)


def test_get_job_not_found(client):
    resp = client.get("/api/v1/jobs/nonexistent")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is False


def test_status_endpoint(client):
    resp = client.get("/api/v1/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["product"] == "ittybitty"
    assert "ffmpeg" in data


def test_tools_endpoint(client):
    resp = client.get("/api/v1/tools")
    assert resp.status_code == 200
    assert resp.json()["count"] == 6


def test_providers_endpoint(client):
    resp = client.get("/api/v1/providers")
    assert resp.status_code == 200
    data = resp.json()
    assert "llm" in data["providers"]
    assert "stock" in data["providers"]
    assert "tts" in data["providers"]


def test_depot_empty(client):
    resp = client.get("/api/v1/depot")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert "summary" in data
    assert isinstance(data["items"], list)


def test_depot_scan(client, tmp_path, monkeypatch):
    out = tmp_path / "depot_out"
    out.mkdir()
    monkeypatch.setenv("VIDEOGEN_OUTPUT_DIR", str(out))
    from videogen_mcp.config.settings import get_settings

    get_settings.cache_clear()
    (out / "aabbccddeeff.mp4").write_bytes(b"\x00" * 32)

    resp = client.post("/api/v1/depot/scan")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["summary"]["imported"] >= 1
    assert any(i["job_id"] == "aabbccddeeff" for i in data["items"])


def test_settings_get(client):
    resp = client.get("/api/v1/settings")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert "settings" in data
    assert "models" in data
    assert len(data["settings"]["llm_providers"]) == 4
    assert "cogvideo_url" in data["settings"]
    assert "stock_hint" in data["settings"]


def test_settings_stock_probe(client):
    resp = client.get("/api/v1/settings/stock")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert "stock" in data
    assert "active_provider" in data["stock"]


def test_settings_save_provider(tmp_path, monkeypatch, client):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "VIDEOGEN_LLM_PROVIDER=openai\nOPENAI_MODEL=gpt-4o-mini\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("VIDEOGEN_ENV_FILE", str(env_file))
    from videogen_mcp.config.settings import get_settings

    get_settings.cache_clear()

    resp = client.put(
        "/api/v1/settings",
        json={"videogen_llm_provider": "deepseek", "deepseek_model": "deepseek-v4-flash"},
    )
    assert resp.status_code == 200
    assert resp.json()["success"] is True
    assert read_env_map_helper(env_file)["VIDEOGEN_LLM_PROVIDER"] == "deepseek"


def read_env_map_helper(path):
    out = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.strip().startswith("#"):
            k, _, v = line.partition("=")
            out[k.strip()] = v
    return out
