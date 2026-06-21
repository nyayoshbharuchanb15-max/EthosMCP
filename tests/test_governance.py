# tests/test_governance.py

import pytest
import os
from src.services.governance import audit_ropa_alignment
from src.config import settings

@pytest.mark.asyncio
async def test_audit_ropa_alignment():
    # Ensure we are pointing to the correct data directory for tests
    # In a real scenario, you might use a separate test data directory
    report = await audit_ropa_alignment()
    assert report.audit_id == "GOV-AUDIT-001"
    assert report.framework == "GDPR"
    # Based on the data/ropa_records.json, we expect some results
    assert len(report.results) > 0
    # Overall status should be WARNING as per the initial ropa_records.json (due to short purpose descriptions)
    assert report.overall_status == "WARNING"
