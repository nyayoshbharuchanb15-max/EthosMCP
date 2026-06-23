from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from src.models.audit import AuditReport, AuditResult
from src.tools import load_metadata_records
from src.utils.crypto import generate_hmac_signature, generate_sha256_hash

# Consent UX friction above this value is treated as non-compliant for withdrawal usability checks.
MAX_WITHDRAWAL_FRICTION_SCORE = 3
# GDPR DSAR fulfillment benchmark: 30-day SLA for response/erasure workflows.
MAX_DSAR_ERASURE_LATENCY_DAYS = 30


async def query_consent_registry() -> AuditReport:
    consent_rows = load_metadata_records("consent_registry.json")
    results: list[AuditResult] = []
    non_compliant = 0
    for row in consent_rows:
        explicit_consent = bool(row.get("explicit_consent"))
        friction = int(row.get("withdrawal_friction_score", 0))
        passed = explicit_consent and friction <= MAX_WITHDRAWAL_FRICTION_SCORE
        if not passed:
            non_compliant += 1
        results.append(
            AuditResult(
                check_id=str(row.get("consent_id", "unknown")),
                status="PASSED" if passed else "FAILED",
                details=f"explicit={explicit_consent}, friction={friction}",
            )
        )

    overall_status = "NON_COMPLIANT" if non_compliant else "COMPLIANT"
    audit_id = "SOV-AUDIT-001"
    framework = "GDPR_DPDP"
    data_state_hash = generate_sha256_hash(json.dumps(consent_rows, sort_keys=True))
    query_hash_digest = generate_sha256_hash(f"{audit_id}:{framework}")
    results_summary = json.dumps(
        [{"check_id": r.check_id, "status": r.status} for r in results],
        sort_keys=True,
    )
    response_signature = generate_hmac_signature(
        f"{audit_id}:{framework}:{overall_status}:{results_summary}"
    )
    return AuditReport(
        audit_id=audit_id,
        framework=framework,
        results=results,
        overall_status=overall_status,
        execution_timestamp=datetime.now(timezone.utc).isoformat(),
        query_hash_digest=query_hash_digest,
        response_signature=response_signature,
        data_state_hash=data_state_hash,
    )


async def simulate_dsar_workflow(dsar_request: dict[str, Any]) -> AuditReport:
    latency_days = int(dsar_request.get("erasure_latency_days", 0))
    passed = latency_days <= MAX_DSAR_ERASURE_LATENCY_DAYS
    result = AuditResult(
        check_id="dsar_erasure_sla",
        status="PASSED" if passed else "FAILED",
        details=f"latency_days={latency_days}",
    )
    overall_status = "COMPLIANT" if passed else "NON_COMPLIANT"
    audit_id = "SOV-AUDIT-DSAR-001"
    framework = "GDPR_DPDP"
    data_state_hash = generate_sha256_hash(json.dumps(dsar_request, sort_keys=True))
    query_hash_digest = generate_sha256_hash(f"{audit_id}:{framework}")
    response_signature = generate_hmac_signature(
        f"{audit_id}:{framework}:{overall_status}:latency_days={latency_days}"
    )
    return AuditReport(
        audit_id=audit_id,
        framework=framework,
        results=[result],
        overall_status=overall_status,
        execution_timestamp=datetime.now(timezone.utc).isoformat(),
        query_hash_digest=query_hash_digest,
        response_signature=response_signature,
        data_state_hash=data_state_hash,
    )
