# tests/test_sovereignty.py

import pytest
from src.services.sovereignty import query_consent_registry, simulate_dsar_workflow

@pytest.mark.asyncio
async def test_query_consent_registry():
    report = await query_consent_registry()
    assert report.audit_id == "SOV-AUDIT-001"
    assert len(report.results) > 0
    # Based on consent_registry.json, user_002 has high friction
    assert report.overall_status == "NON_COMPLIANT"

@pytest.mark.asyncio
async def test_simulate_dsar_workflow_compliant():
    dsar_request = {"user_id": "user_001", "request_type": "erasure", "erasure_latency_days": 20}
    report = await simulate_dsar_workflow(dsar_request)
    assert report.overall_status == "COMPLIANT"
    assert report.results[0].status == "PASSED"

@pytest.mark.asyncio
async def test_simulate_dsar_workflow_non_compliant():
    dsar_request = {"user_id": "user_001", "request_type": "erasure", "erasure_latency_days": 40}
    report = await simulate_dsar_workflow(dsar_request)
    assert report.overall_status == "NON_COMPLIANT"
    assert report.results[0].status == "FAILED"
