from src.server import initialize_payload, tools_list
from src.workflow import ResourceOrchestrator


def test_workflow_snapshot_contains_architecture_components():
    orchestrator = ResourceOrchestrator()
    snapshot = orchestrator.workflow_snapshot()
    assert "contexts" in snapshot
    assert "tools" in snapshot
    assert snapshot["mode"] == "read-only-metadata"


def test_documented_tools_are_registered():
    names = {tool.get("name") for tool in tools_list()}
    assert "get_ropa_records" in names
    assert "analyze_data_flow" in names
    assert "query_consent_registry" in names
    assert "simulate_dsar_workflow" in names


def test_initialize_payload_server_info_present():
    payload = initialize_payload()
    assert payload["serverInfo"]["name"] == "EthosMCP"
    assert "tools" in payload["capabilities"]
