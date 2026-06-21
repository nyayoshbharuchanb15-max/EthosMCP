# tests/test_security.py

import pytest
from src.services.security import audit_encryption_coverage

@pytest.mark.asyncio
async def test_audit_encryption_coverage():
    report = await audit_encryption_coverage()
    assert report.audit_id == "SEC-AUDIT-001"
    assert len(report.results) > 0
    # Based on security_config.json, SYS-002 is not encrypted at rest
    assert report.overall_status == "NON_COMPLIANT"
