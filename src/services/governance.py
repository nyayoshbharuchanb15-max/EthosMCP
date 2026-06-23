from __future__ import annotations

from datetime import datetime, timezone

from src.models.audit import AuditReport, AuditResult
from src.tools import load_metadata_records


async def get_ropa_records() -> AuditReport:
    records = load_metadata_records("ropa_records.json")
    coverage = len(records)
    return AuditReport(
        audit_id="GOV-AUDIT-001",
        framework="GDPR",
        results=[AuditResult(check_id="ropa_records_count", status="PASSED", details=str(coverage))],
        overall_status="WARNING",
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
        passed = len(purpose) >= 10
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
