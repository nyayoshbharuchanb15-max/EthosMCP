import pytest
from src.services.sovereignty import query_consent_registry, simulate_dsar_workflow

@pytest.mark.asyncio
async def test_query_consent_registry_compliant():
    consent_data = {"explicit_consent": True}
    report = await query_consent_registry(consent_data)
    assert report.overall_status == "COMPLIANT"
    assert len(report.results) == 1
    assert report.results[0].status == "PASSED"

@pytest.mark.asyncio
async def test_query_consent_registry_non_compliant():
    consent_data = {"explicit_consent": False}
    report = await query_consent_registry(consent_data)
    assert report.overall_status == "NON_COMPLIANT"
    assert len(report.results) == 1
    assert report.results[0].status == "FAILED"
    assert "Explicit consent not recorded" in report.results[0].details

@pytest.mark.asyncio
async def test_simulate_dsar_workflow_compliant():
    dsar_request = {"erasure_latency_days": 20}
    report = await simulate_dsar_workflow(dsar_request)
    assert report.overall_status == "COMPLIANT"
    assert len(report.results) == 1
    assert report.results[0].status == "PASSED"

@pytest.mark.asyncio
async def test_simulate_dsar_workflow_non_compliant():
    dsar_request = {"erasure_latency_days": 40}
    report = await simulate_dsar_workflow(dsar_request)
    assert report.overall_status == "NON_COMPLIANT"
    assert len(report.results) == 1
    assert report.results[0].status == "FAILED"
    assert "Erasure latency exceeds 30 days" in report.results[0].details
