"""FastMCP application for EthosMCP.

This module exposes all audit tools through the MCP protocol so that any
MCP-compatible client (Claude Desktop, Cursor, etc.) can invoke them.  The
same service functions that back the FastAPI HTTP endpoints are reused here,
keeping business logic in one place.
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from mcp.server.fastmcp import FastMCP

from src.config import settings
from src.services import governance, localization, security, sovereignty
from src.services import data_purpose

mcp = FastMCP(
    settings.app_name,
    instructions=(
        "Zero-trust AI governance and data-protection compliance audit framework. "
        "All tools operate in read-only metadata mode and never mutate source systems."
    ),
)


# ---------------------------------------------------------------------------
# MCP Resources (static context for LLM clients)
# ---------------------------------------------------------------------------


@mcp.resource("policy://eu-ai-act-summary")
async def get_eu_ai_act_policy() -> str:
    """EU AI Act Summary: core compliance rules for EthosMCP.

    Returns the zero-trust policy document that governs all AI requests processed
    by this server, covering data-lineage verification and purpose-limitation rules.
    """
    return (
        "POLICY DOCUMENT: All AI requests must verify data lineage and purpose "
        "limitation before execution. Zero-trust architecture enforced. "
        "Datasets must be used only for explicitly allowed purposes as defined "
        "in the dataset purpose registry. Prohibited purposes are blocked regardless "
        "of data-subject consent. Compliance is governed by the EU AI Act and GDPR."
    )


# ---------------------------------------------------------------------------
# Phase 1 – Governance & ROPA
# ---------------------------------------------------------------------------


@mcp.tool()
async def get_ropa_records() -> dict[str, Any]:
    """Retrieve Records of Processing Activities (ROPA) metadata for governance baseline."""
    return asdict(await governance.get_ropa_records())


@mcp.tool()
async def audit_ropa_alignment() -> dict[str, Any]:
    """Audit ROPA records for purpose-limitation and legal-basis compliance."""
    return asdict(await governance.audit_ropa_alignment())


# ---------------------------------------------------------------------------
# Phase 2 – Localization & Data Residency
# ---------------------------------------------------------------------------


@mcp.tool()
async def analyze_data_flow() -> dict[str, Any]:
    """Analyze metadata-only data-flow localization posture for cross-border transfer compliance."""
    return asdict(await localization.analyze_data_flow())


# ---------------------------------------------------------------------------
# Phase 3 – Consent & DSAR
# ---------------------------------------------------------------------------


@mcp.tool()
async def query_consent_registry() -> dict[str, Any]:
    """Evaluate consent metadata state-machine evidence and withdrawal-friction scores."""
    return asdict(await sovereignty.query_consent_registry())


@mcp.tool()
async def simulate_dsar_workflow(erasure_latency_days: int = 0) -> dict[str, Any]:
    """Simulate DSAR propagation across system layers without executing deletions.

    Args:
        erasure_latency_days: Expected erasure SLA in days (GDPR benchmark: ≤30).
    """
    return asdict(
        await sovereignty.simulate_dsar_workflow({"erasure_latency_days": erasure_latency_days})
    )


# ---------------------------------------------------------------------------
# Phase 4 – Security & Encryption
# ---------------------------------------------------------------------------


@mcp.tool()
async def audit_encryption_coverage() -> dict[str, Any]:
    """Audit encryption metadata coverage for data at rest (AES-256) and in transit (TLS 1.3)."""
    return asdict(await security.audit_encryption_coverage())


# ---------------------------------------------------------------------------
# Phase 5 – Data Purpose Verification (EU AI Act / GDPR purpose-limitation)
# ---------------------------------------------------------------------------


@mcp.tool()
async def verify_data_purpose(dataset_id: str, requested_purpose: str) -> dict[str, Any]:
    """Verify that a requested data-usage purpose is permitted for the given dataset.

    Checks the dataset-purpose registry against EU AI Act and GDPR purpose-limitation
    rules.  Returns COMPLIANT when the purpose is explicitly allowed and not prohibited,
    NON_COMPLIANT otherwise.

    Args:
        dataset_id: Identifier of the dataset (e.g. DS-CUSTOMER-001).
        requested_purpose: Intended use of the dataset (e.g. billing, model_training).
    """
    return asdict(
        await data_purpose.verify_data_purpose(
            {"dataset_id": dataset_id, "requested_purpose": requested_purpose}
        )
    )
