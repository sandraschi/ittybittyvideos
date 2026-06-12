from videogen_mcp.services.activity_log import clear_logs, log_activity, query_logs


def test_query_logs_empty():
    clear_logs()
    result = query_logs(limit=10)
    assert result["entries"] == []
    assert result["total"] == 0


def test_log_activity_and_filter():
    clear_logs()
    log_activity("pipeline", "job abc started", level="INFO", meta={"job_id": "abc"})
    log_activity("server", "debug trace", level="DEBUG")
    result = query_logs(kind="pipeline", limit=10)
    assert result["total"] == 1
    assert result["entries"][0]["detail"] == "job abc started"


def test_logs_api_routes():
    from fastapi.testclient import TestClient

    from videogen_mcp.server import rest

    client = TestClient(rest)
    clear_logs()
    log_activity("system", "test entry", level="INFO")

    resp = client.get("/api/logs?limit=10")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    assert any(e["detail"] == "test entry" for e in data["entries"])

    stats = client.get("/api/logs/stats")
    assert stats.status_code == 200
    assert stats.json()["total"] >= 1

    cleared = client.delete("/api/logs")
    assert cleared.status_code == 200
    assert client.get("/api/logs").json()["total"] == 1  # clear logs itself
