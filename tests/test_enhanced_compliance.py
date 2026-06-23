# tests/test_enhanced_compliance.py
"""
Tests for enhanced compliance checks:
  - Governance: legal-basis and data-categories presence (GDPR Art. 30)
  - Localization: legal-mechanism validation for cross-border transfers (GDPR Ch. V)
  - Security: DPA-signing check (GDPR Art. 28) and breach-detection posture
"""

import pytest
from src.services.governance import audit_ropa_alignment
from src.services.localization import analyze_data_flow
from src.services.security import audit_encryption_coverage


# ---------------------------------------------------------------------------
# Governance – legal-basis and data-categories presence
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_ropa_result_details_include_legal_basis():
    """Each ROPA result details string must expose the legal_basis value."""
    report = await audit_ropa_alignment()
    for result in report.results:
        assert "legal_basis=" in result.details, (
            f"result {result.check_id} details should include legal_basis: {result.details}"
        )


@pytest.mark.asyncio
async def test_ropa_result_details_include_data_categories_flag():
    """Each ROPA result details string must expose data_categories_present."""
    report = await audit_ropa_alignment()
    for result in report.results:
        assert "data_categories_present=" in result.details, (
            f"result {result.check_id} details should include data_categories_present: {result.details}"
        )


# ---------------------------------------------------------------------------
# Localization – legal-mechanism validation for cross-border transfers
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_localization_result_details_include_mechanism():
    """Each flow result must expose the legal_mechanism in its details string."""
    report = await analyze_data_flow()
    for result in report.results:
        assert "mechanism=" in result.details, (
            f"result {result.check_id} details should include mechanism: {result.details}"
        )


@pytest.mark.asyncio
async def test_unauthorized_cross_border_flow_is_failed():
    """FLOW-IN-US-001 (authorized=false) must produce a FAILED result."""
    report = await analyze_data_flow()
    india_flow = next(
        (r for r in report.results if r.check_id == "FLOW-IN-US-001"),
        None,
    )
    assert india_flow is not None, "FLOW-IN-US-001 should be present in results"
    assert india_flow.status == "FAILED"


@pytest.mark.asyncio
async def test_authorized_intra_region_flow_is_passed():
    """FLOW-EU-EU-001 (same region, authorized=true) must produce a PASSED result."""
    report = await analyze_data_flow()
    eu_eu_flow = next(
        (r for r in report.results if r.check_id == "FLOW-EU-EU-001"),
        None,
    )
    assert eu_eu_flow is not None, "FLOW-EU-EU-001 should be present in results"
    assert eu_eu_flow.status == "PASSED"


@pytest.mark.asyncio
async def test_authorized_cross_border_flow_with_sccs_is_passed():
    """FLOW-EU-US-001 (cross-border, authorized=true, SCCs) must produce a PASSED result."""
    report = await analyze_data_flow()
    eu_us_flow = next(
        (r for r in report.results if r.check_id == "FLOW-EU-US-001"),
        None,
    )
    assert eu_us_flow is not None, "FLOW-EU-US-001 should be present in results"
    assert eu_us_flow.status == "PASSED"


# ---------------------------------------------------------------------------
# Security – DPA-signing (GDPR Art. 28) and breach-detection
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_security_result_details_include_all_dpa_signed():
    """Security result details must expose the all_dpa_signed flag."""
    report = await audit_encryption_coverage()
    for result in report.results:
        assert "all_dpa_signed=" in result.details, (
            f"result {result.check_id} details should include all_dpa_signed: {result.details}"
        )


@pytest.mark.asyncio
async def test_security_result_details_include_breach_detection():
    """Security result details must expose the breach_detection flag."""
    report = await audit_encryption_coverage()
    for result in report.results:
        assert "breach_detection=" in result.details, (
            f"result {result.check_id} details should include breach_detection: {result.details}"
        )


@pytest.mark.asyncio
async def test_sys001_fails_due_to_unsigned_dpa():
    """SYS-001 has an unsigned DPA for PROC-002 and must therefore be FAILED."""
    report = await audit_encryption_coverage()
    sys001 = next((r for r in report.results if r.check_id == "SYS-001"), None)
    assert sys001 is not None, "SYS-001 should be present in results"
    assert sys001.status == "FAILED", (
        "SYS-001 must fail because PROC-002's DPA is not signed"
    )


@pytest.mark.asyncio
async def test_sys002_fails_due_to_missing_at_rest_encryption():
    """SYS-002 lacks AES-256 at-rest encryption and must therefore be FAILED."""
    report = await audit_encryption_coverage()
    sys002 = next((r for r in report.results if r.check_id == "SYS-002"), None)
    assert sys002 is not None, "SYS-002 should be present in results"
    assert sys002.status == "FAILED"
