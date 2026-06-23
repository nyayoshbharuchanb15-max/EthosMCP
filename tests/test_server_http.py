# tests/test_server_http.py
"""HTTP endpoint tests for the EthosMCP FastAPI server."""

from __future__ import annotations

from fastapi.testclient import TestClient

from src.server import app

client = TestClient(app)


# ---------------------------------------------------------------------------
# Health / meta endpoints
# ---------------------------------------------------------------------------


def test_healthz_returns_ok():
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_mcp_initialize_returns_protocol_version():
    response = client.post("/mcp/initialize")
    assert response.status_code == 200
    body = response.json()
    assert body["protocolVersion"] == "2025-06-18"
    assert body["serverInfo"]["name"] == "EthosMCP"
    assert "tools" in body["capabilities"]


def test_well_known_oauth_contains_issuer():
    response = client.get("/.well-known/oauth-authorization-server")
    assert response.status_code == 200
    body = response.json()
    assert "issuer" in body
    assert "token_endpoint" in body


def test_audit_export_returns_metadata_only():
    response = client.get("/audit/export")
    assert response.status_code == 200
    assert response.json()["status"] == "metadata-only"


# ---------------------------------------------------------------------------
# Tools list & workflow snapshot
# ---------------------------------------------------------------------------


def test_tools_list_contains_expected_tools():
    response = client.get("/tools/list")
    assert response.status_code == 200
    names = {tool["name"] for tool in response.json()}
    assert "get_ropa_records" in names
    assert "audit_ropa_alignment" in names
    assert "analyze_data_flow" in names
    assert "query_consent_registry" in names
    assert "simulate_dsar_workflow" in names
    assert "audit_encryption_coverage" in names


def test_workflow_snapshot_shape():
    response = client.get("/workflow/snapshot")
    assert response.status_code == 200
    body = response.json()
    assert "contexts" in body
    assert "tools" in body
    assert body["mode"] == "read-only-metadata"


# ---------------------------------------------------------------------------
# Tool invocation – happy paths
# ---------------------------------------------------------------------------


def test_invoke_get_ropa_records():
    response = client.post("/tools/invoke/get_ropa_records")
    assert response.status_code == 200
    body = response.json()
    assert "result" in body
    assert body["result"]["audit_id"] == "GOV-ROPA-001"


def test_invoke_analyze_data_flow():
    response = client.post("/tools/invoke/analyze_data_flow")
    assert response.status_code == 200
    body = response.json()
    assert body["result"]["framework"] == "GDPR_DPDP"


def test_invoke_simulate_dsar_workflow_compliant():
    payload = {"erasure_latency_days": 20}
    response = client.post("/tools/invoke/simulate_dsar_workflow", json=payload)
    assert response.status_code == 200
    assert response.json()["result"]["overall_status"] == "COMPLIANT"


def test_invoke_audit_encryption_coverage():
    response = client.post("/tools/invoke/audit_encryption_coverage")
    assert response.status_code == 200
    body = response.json()
    assert body["result"]["audit_id"] == "SEC-AUDIT-001"


# ---------------------------------------------------------------------------
# Tool invocation – failure paths
# ---------------------------------------------------------------------------


def test_invoke_unknown_tool_returns_404():
    response = client.post("/tools/invoke/nonexistent_tool")
    assert response.status_code == 404
    assert "Unknown tool" in response.json()["detail"]


def test_invoke_simulate_dsar_workflow_non_compliant():
    payload = {"erasure_latency_days": 45}
    response = client.post("/tools/invoke/simulate_dsar_workflow", json=payload)
    assert response.status_code == 200
    assert response.json()["result"]["overall_status"] == "NON_COMPLIANT"
