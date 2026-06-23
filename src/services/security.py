from __future__ import annotations

from datetime import datetime, timezone

from src.models.audit import AuditReport, AuditResult
from src.tools import load_metadata_records


async def audit_encryption_coverage() -> AuditReport:
    systems = load_metadata_records("security_config.json")
    results: list[AuditResult] = []
    non_compliant = 0
    for system in systems:
        at_rest = bool(system.get("at_rest_aes256"))
        in_transit = bool(system.get("in_transit_tls13"))
        passed = at_rest and in_transit
        if not passed:
            non_compliant += 1
        results.append(
            AuditResult(
                check_id=str(system.get("system_id", "unknown")),
                status="PASSED" if passed else "FAILED",
                details=f"at_rest={at_rest}, in_transit={in_transit}",
            )
        )

    return AuditReport(
        audit_id="SEC-AUDIT-001",
        framework="ISO42001_GDPR",
        results=results,
        overall_status="NON_COMPLIANT" if non_compliant else "COMPLIANT",
        execution_timestamp=datetime.now(timezone.utc).isoformat(),
        query_hash_digest="metadata-only",
        response_signature="unsigned-prototype",
        data_state_hash="metadata-snapshot",
    )
