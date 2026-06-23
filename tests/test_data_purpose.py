# tests/test_data_purpose.py
"""Tests for the verify_data_purpose service and HTTP endpoint."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from src.server import app
from src.services.data_purpose import verify_data_purpose

client = TestClient(app)

_HEX_DIGEST_LENGTH = 64


# ---------------------------------------------------------------------------
# Service-level tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_allowed_purpose_returns_compliant():
    report = await verify_data_purpose(
        {"dataset_id": "DS-CUSTOMER-001", "requested_purpose": "billing"}
    )
    assert report.audit_id == "PURPOSE-AUDIT-001"
    assert report.framework == "EU_AI_ACT_GDPR"
    assert report.overall_status == "COMPLIANT"
    assert report.results[0].status == "PASSED"


@pytest.mark.asyncio
async def test_prohibited_purpose_returns_non_compliant():
    report = await verify_data_purpose(
        {"dataset_id": "DS-CUSTOMER-001", "requested_purpose": "third_party_marketing"}
    )
    assert report.overall_status == "NON_COMPLIANT"
    assert report.results[0].status == "FAILED"


@pytest.mark.asyncio
async def test_unknown_dataset_returns_non_compliant():
    report = await verify_data_purpose(
        {"dataset_id": "DS-UNKNOWN-999", "requested_purpose": "billing"}
    )
    assert report.overall_status == "NON_COMPLIANT"
    assert report.results[0].status == "FAILED"
    assert "unknown_dataset" in report.results[0].details


@pytest.mark.asyncio
async def test_purpose_not_in_allowed_list_is_non_compliant():
    """A purpose that is neither explicitly allowed nor prohibited must be non-compliant."""
    report = await verify_data_purpose(
        {"dataset_id": "DS-CUSTOMER-001", "requested_purpose": "research"}
    )
    assert report.overall_status == "NON_COMPLIANT"
    assert report.results[0].status == "FAILED"


@pytest.mark.asyncio
async def test_ai_training_allowed_purpose():
    report = await verify_data_purpose(
        {"dataset_id": "DS-AI-TRAINING-001", "requested_purpose": "model_training"}
    )
    assert report.overall_status == "COMPLIANT"


@pytest.mark.asyncio
async def test_result_details_include_dataset_and_purpose():
    report = await verify_data_purpose(
        {"dataset_id": "DS-TELEMETRY-001", "requested_purpose": "analytics"}
    )
    assert "dataset_id=" in report.results[0].details
    assert "requested_purpose=" in report.results[0].details


# ---------------------------------------------------------------------------
# Crypto / signature integrity tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_verify_data_purpose_produces_real_signatures():
    report = await verify_data_purpose(
        {"dataset_id": "DS-CUSTOMER-001", "requested_purpose": "billing"}
    )
    assert len(report.response_signature) == _HEX_DIGEST_LENGTH
    assert len(report.data_state_hash) == _HEX_DIGEST_LENGTH
    assert len(report.query_hash_digest) == _HEX_DIGEST_LENGTH


@pytest.mark.asyncio
async def test_signatures_differ_for_different_outcomes():
    compliant = await verify_data_purpose(
        {"dataset_id": "DS-CUSTOMER-001", "requested_purpose": "billing"}
    )
    non_compliant = await verify_data_purpose(
        {"dataset_id": "DS-CUSTOMER-001", "requested_purpose": "third_party_marketing"}
    )
    assert compliant.response_signature != non_compliant.response_signature


# ---------------------------------------------------------------------------
# HTTP endpoint tests
# ---------------------------------------------------------------------------


def test_tools_list_includes_verify_data_purpose():
    response = client.get("/tools/list")
    assert response.status_code == 200
    names = {tool["name"] for tool in response.json()}
    assert "verify_data_purpose" in names


def test_invoke_verify_data_purpose_compliant():
    payload = {"dataset_id": "DS-CUSTOMER-001", "requested_purpose": "billing"}
    response = client.post("/tools/invoke/verify_data_purpose", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["result"]["overall_status"] == "COMPLIANT"
    assert body["result"]["audit_id"] == "PURPOSE-AUDIT-001"


def test_invoke_verify_data_purpose_non_compliant():
    payload = {"dataset_id": "DS-CUSTOMER-001", "requested_purpose": "third_party_marketing"}
    response = client.post("/tools/invoke/verify_data_purpose", json=payload)
    assert response.status_code == 200
    assert response.json()["result"]["overall_status"] == "NON_COMPLIANT"
