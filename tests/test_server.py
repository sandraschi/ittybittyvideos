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


def test_providers_endpoint(client):
    resp = client.get("/api/v1/providers")
    assert resp.status_code == 200
    data = resp.json()
    assert "llm" in data["providers"]
    assert "stock" in data["providers"]
    assert "tts" in data["providers"]
