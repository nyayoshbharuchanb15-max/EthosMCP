# tests/test_governance.py

import pytest
from src.services.governance import audit_ropa_alignment
from src.models import RopaEntry

@pytest.mark.asyncio
async def test_audit_ropa_alignment_compliant():
    ropa_data = [
        RopaEntry(
            ropa_id="ROPA-001",
            processing_activity="Customer Data Collection",
            legal_basis="Consent",
            data_categories=["Personal Identifiable Information"],
            purpose="Marketing",
            department_owner="Marketing"
        )
    ]
    report = await audit_ropa_alignment(ropa_data)
    assert report.overall_status == "COMPLIANT"
    assert len(report.results) == 1
    assert report.results[0].status == "PASSED"

@pytest.mark.asyncio
async def test_audit_ropa_alignment_non_compliant():
    ropa_data = [
        RopaEntry(
            ropa_id="ROPA-002",
            processing_activity="Internal Analytics",
            legal_basis="", # Missing legal basis
            data_categories=["Usage Data"],
            purpose="Product Improvement",
            department_owner="Engineering"
        )
    ]
    report = await audit_ropa_alignment(ropa_data)
    assert report.overall_status == "NON_COMPLIANT"
    assert len(report.results) == 1
    assert report.results[0].status == "FAILED"
    assert "Missing legal basis" in report.results[0].details
