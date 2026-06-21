# tests/test_security.py

import pytest
from src.services.security import audit_encryption_coverage

@pytest.mark.asyncio
async def test_audit_encryption_coverage_compliant():
    encryption_report = {"at_rest_aes256": True}
    report = await audit_encryption_coverage(encryption_report)
    assert report.overall_status == "COMPLIANT"
    assert len(report.results) == 1
    assert report.results[0].status == "PASSED"

@pytest.mark.asyncio
async def test_audit_encryption_coverage_non_compliant():
    encryption_report = {"at_rest_aes256": False}
    report = await audit_encryption_coverage(encryption_report)
    assert report.overall_status == "NON_COMPLIANT"
    assert len(report.results) == 1
    assert report.results[0].status == "FAILED"
    assert "AES-256 encryption at rest not confirmed" in report.results[0].details
