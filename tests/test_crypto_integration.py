# tests/test_crypto_integration.py
"""
Tests that all audit services produce real cryptographic signatures and hashes
instead of placeholder strings, verifying the crypto integration layer.
"""

import pytest
from src.services.governance import audit_ropa_alignment, get_ropa_records
from src.services.localization import analyze_data_flow
from src.services.security import audit_encryption_coverage
from src.services.sovereignty import query_consent_registry, simulate_dsar_workflow

# HMAC-SHA256 and SHA256 both produce 64-character hex digests.
_HEX_DIGEST_LENGTH = 64


@pytest.mark.asyncio
async def test_governance_ropa_has_real_signatures():
    report = await audit_ropa_alignment()
    assert len(report.response_signature) == _HEX_DIGEST_LENGTH, "response_signature must be a SHA256 hex digest"
    assert len(report.data_state_hash) == _HEX_DIGEST_LENGTH, "data_state_hash must be a SHA256 hex digest"
    assert len(report.query_hash_digest) == _HEX_DIGEST_LENGTH, "query_hash_digest must be a SHA256 hex digest"


@pytest.mark.asyncio
async def test_get_ropa_records_has_real_signatures():
    report = await get_ropa_records()
    assert len(report.response_signature) == _HEX_DIGEST_LENGTH
    assert len(report.data_state_hash) == _HEX_DIGEST_LENGTH
    assert len(report.query_hash_digest) == _HEX_DIGEST_LENGTH


@pytest.mark.asyncio
async def test_localization_has_real_signatures():
    report = await analyze_data_flow()
    assert len(report.response_signature) == _HEX_DIGEST_LENGTH
    assert len(report.data_state_hash) == _HEX_DIGEST_LENGTH
    assert len(report.query_hash_digest) == _HEX_DIGEST_LENGTH


@pytest.mark.asyncio
async def test_security_has_real_signatures():
    report = await audit_encryption_coverage()
    assert len(report.response_signature) == _HEX_DIGEST_LENGTH
    assert len(report.data_state_hash) == _HEX_DIGEST_LENGTH
    assert len(report.query_hash_digest) == _HEX_DIGEST_LENGTH


@pytest.mark.asyncio
async def test_sovereignty_consent_registry_has_real_signatures():
    report = await query_consent_registry()
    assert len(report.response_signature) == _HEX_DIGEST_LENGTH
    assert len(report.data_state_hash) == _HEX_DIGEST_LENGTH
    assert len(report.query_hash_digest) == _HEX_DIGEST_LENGTH


@pytest.mark.asyncio
async def test_sovereignty_dsar_has_real_signatures():
    dsar_request = {"user_id": "user_001", "request_type": "erasure", "erasure_latency_days": 10}
    report = await simulate_dsar_workflow(dsar_request)
    assert len(report.response_signature) == _HEX_DIGEST_LENGTH
    assert len(report.data_state_hash) == _HEX_DIGEST_LENGTH
    assert len(report.query_hash_digest) == _HEX_DIGEST_LENGTH


@pytest.mark.asyncio
async def test_signatures_differ_between_compliant_and_non_compliant_dsar():
    """Response signatures must differ when audit outcomes differ."""
    compliant = await simulate_dsar_workflow({"erasure_latency_days": 10})
    non_compliant = await simulate_dsar_workflow({"erasure_latency_days": 45})
    assert compliant.response_signature != non_compliant.response_signature
