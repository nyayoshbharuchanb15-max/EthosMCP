# tests/test_localization.py

import pytest
from src.services.localization import analyze_data_flow

@pytest.mark.asyncio
async def test_analyze_data_flow_compliant():
    data_flow_map = {"eu_data_in_us": False}
    report = await analyze_data_flow(data_flow_map)
    assert report.overall_status == "COMPLIANT"
    assert len(report.results) == 1
    assert report.results[0].status == "PASSED"

@pytest.mark.asyncio
async def test_analyze_data_flow_non_compliant():
    data_flow_map = {"eu_data_in_us": True}
    report = await analyze_data_flow(data_flow_map)
    assert report.overall_status == "NON_COMPLIANT"
    assert len(report.results) == 1
    assert report.results[0].status == "FAILED"
    assert "EU data detected in US without SCCs" in report.results[0].details
