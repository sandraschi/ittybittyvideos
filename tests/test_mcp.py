"""MCP registry and catalog consistency tests."""

from videogen_mcp.mcp_registry import MCP_TOOL_CATALOG, MCP_WORKFLOW_HINTS, mcp_help_payload, mcp_tool_count
from videogen_mcp.services.credits import normalize_credits_id
from videogen_mcp.services.intros import normalize_intro_id


def test_mcp_catalog_has_core_tools():
    names = {t["name"] for t in MCP_TOOL_CATALOG}
    for required in (
        "videogen_help",
        "videogen_generate",
        "videogen_structures",
        "videogen_intros",
        "videogen_credits",
        "videogen_visual_look",
        "videogen_depot",
        "videogen_publish_pack",
    ):
        assert required in names


def test_mcp_tool_count_matches_catalog():
    assert mcp_tool_count() == len(MCP_TOOL_CATALOG) == 16


def test_mcp_help_payload():
    payload = mcp_help_payload(mcp_enabled=True, version="0.0.0-test")
    assert payload["success"] is True
    assert payload["tool_count"] == 16
    assert len(payload["workflow_hints"]) == len(MCP_WORKFLOW_HINTS)
    assert payload["mcp_endpoint"] == "/mcp"


def test_normalize_intro_id_prefix():
    assert normalize_intro_id("intro:bluey-horror-contrast") == "bluey-horror-contrast"
    assert normalize_intro_id("documentary-gravitas") == "documentary-gravitas"


def test_normalize_credits_id_prefix():
    assert normalize_credits_id("credits:absurd-pixar") == "absurd-pixar"
    assert normalize_credits_id("absurd-pixar") == "absurd-pixar"


def test_tools_endpoint_matches_catalog(client):
    from videogen_mcp.mcp_registry import mcp_tool_count

    resp = client.get("/api/v1/tools")
    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] == mcp_tool_count()
    assert len(data["tools"]) == mcp_tool_count()


def test_status_tool_count(client):
    from videogen_mcp.mcp_registry import mcp_tool_count

    resp = client.get("/api/v1/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["mcp_enabled"] is True
    assert data["tool_count"] == mcp_tool_count()


def test_health_mcp_fields(client):
    from videogen_mcp.mcp_registry import mcp_tool_count

    resp = client.get("/health")
    data = resp.json()
    assert data["mcp"] is True
    assert data["tool_count"] == mcp_tool_count()


def test_structures_endpoint(client):
    resp = client.get("/api/v1/structures")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["count"] >= 1


def test_intro_packs_endpoint(client):
    resp = client.get("/api/v1/intros/packs")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["count"] >= 1


def test_credits_packs_endpoint(client):
    resp = client.get("/api/v1/credits/packs")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["count"] >= 1


def test_visual_look_catalog_endpoint(client):
    resp = client.get("/api/v1/visual-look/catalog")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert "catalog" in data
