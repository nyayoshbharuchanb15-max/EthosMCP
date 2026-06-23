from __future__ import annotations

from datetime import datetime, timezone

from src.models.audit import AuditReport, AuditResult
from src.tools import load_metadata_records

MIN_PURPOSE_DESCRIPTION_LENGTH = 10


async def get_ropa_records() -> AuditReport:
    records = load_metadata_records("ropa_records.json")
    coverage = len(records)
    overall_status = "PASSED" if coverage > 0 else "WARNING"
    return AuditReport(
        audit_id="GOV-ROPA-001",
        framework="GDPR",
        results=[AuditResult(check_id="ropa_records_count", status="COMPLIANT", details=str(coverage))],
        overall_status=overall_status,
        execution_timestamp=datetime.now(timezone.utc).isoformat(),
        query_hash_digest="metadata-only",
        response_signature="unsigned-prototype",
        data_state_hash="metadata-snapshot",
    )


async def audit_ropa_alignment() -> AuditReport:
    records = load_metadata_records("ropa_records.json")
    results: list[AuditResult] = []
    warning_count = 0
    for record in records:
        purpose = record.get("purpose", "")
        # Keep a deterministic quality floor for purpose-limitation metadata completeness.
        passed = len(purpose) >= MIN_PURPOSE_DESCRIPTION_LENGTH
        status = "PASSED" if passed else "WARNING"
        if not passed:
            warning_count += 1
        results.append(
            AuditResult(
                check_id=str(record.get("ropa_id", "unknown")),
                status=status,
                details=f"purpose={purpose}",
            )
        )

    overall_status = "WARNING" if warning_count else "PASSED"
    return AuditReport(
        audit_id="GOV-AUDIT-001",
        framework="GDPR",
        results=results,
        overall_status=overall_status,
        execution_timestamp=datetime.now(timezone.utc).isoformat(),
        query_hash_digest="metadata-only",
        response_signature="unsigned-prototype",
        data_state_hash="metadata-snapshot",
    )
