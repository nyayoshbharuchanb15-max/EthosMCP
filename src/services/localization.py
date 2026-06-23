from __future__ import annotations

from datetime import datetime, timezone

from src.models.audit import AuditReport, AuditResult
from src.tools import load_metadata_records


async def analyze_data_flow() -> AuditReport:
    flows = load_metadata_records("data_flow_map.json")
    results: list[AuditResult] = []
    non_compliant = 0
    for flow in flows:
        authorized = bool(flow.get("authorized"))
        status = "PASSED" if authorized else "FAILED"
        if not authorized:
            non_compliant += 1
        results.append(
            AuditResult(
                check_id=str(flow.get("flow_id", "unknown")),
                status=status,
                details=f"{flow.get('source_region')}->{flow.get('destination_region')}",
            )
        )

    return AuditReport(
        audit_id="LOC-AUDIT-001",
        framework="GDPR_DPDP",
        results=results,
        overall_status="NON_COMPLIANT" if non_compliant else "COMPLIANT",
        execution_timestamp=datetime.now(timezone.utc).isoformat(),
        query_hash_digest="metadata-only",
        response_signature="unsigned-prototype",
        data_state_hash="metadata-snapshot",
    )
