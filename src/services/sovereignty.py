from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from src.models.audit import AuditReport, AuditResult
from src.tools import load_metadata_records


async def query_consent_registry() -> AuditReport:
    consent_rows = load_metadata_records("consent_registry.json")
    results: list[AuditResult] = []
    non_compliant = 0
    for row in consent_rows:
        explicit_consent = bool(row.get("explicit_consent"))
        friction = int(row.get("withdrawal_friction_score", 0))
        passed = explicit_consent and friction <= 3
        if not passed:
            non_compliant += 1
        results.append(
            AuditResult(
                check_id=str(row.get("consent_id", "unknown")),
                status="PASSED" if passed else "FAILED",
                details=f"explicit={explicit_consent}, friction={friction}",
            )
        )

    return AuditReport(
        audit_id="SOV-AUDIT-001",
        framework="GDPR_DPDP",
        results=results,
        overall_status="NON_COMPLIANT" if non_compliant else "COMPLIANT",
        execution_timestamp=datetime.now(timezone.utc).isoformat(),
        query_hash_digest="metadata-only",
        response_signature="unsigned-prototype",
        data_state_hash="metadata-snapshot",
    )


async def simulate_dsar_workflow(dsar_request: dict[str, Any]) -> AuditReport:
    latency_days = int(dsar_request.get("erasure_latency_days", 0))
    passed = latency_days <= 30
    result = AuditResult(
        check_id="dsar_erasure_sla",
        status="PASSED" if passed else "FAILED",
        details=f"latency_days={latency_days}",
    )
    return AuditReport(
        audit_id="SOV-AUDIT-DSAR-001",
        framework="GDPR_DPDP",
        results=[result],
        overall_status="COMPLIANT" if passed else "NON_COMPLIANT",
        execution_timestamp=datetime.now(timezone.utc).isoformat(),
        query_hash_digest="metadata-only",
        response_signature="unsigned-prototype",
        data_state_hash="metadata-snapshot",
    )
