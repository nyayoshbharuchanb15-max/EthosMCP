# tests/test_localization.py

import pytest
from src.services.localization import analyze_data_flow

@pytest.mark.asyncio
async def test_analyze_data_flow():
    report = await analyze_data_flow()
    assert report.audit_id == "LOC-AUDIT-001"
    assert report.framework == "GDPR_DPDP"
    assert len(report.results) > 0
    # Based on data_flow_map.json, there is a non-authorized flow for India
    assert report.overall_status == "NON_COMPLIANT"
