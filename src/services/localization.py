from __future__ import annotations

import json
from datetime import datetime, timezone

from src.models.audit import AuditReport, AuditResult
from src.tools import load_metadata_records
from src.utils.crypto import generate_hmac_signature, generate_sha256_hash

# Legal mechanisms that satisfy cross-border transfer requirements under GDPR/DPDP.
_VALID_CROSS_BORDER_MECHANISMS = {"SCCs", "BCRs", "Adequacy Decision", "Consent", "Derogation"}


async def analyze_data_flow() -> AuditReport:
    flows = load_metadata_records("data_flow_map.json")
    results: list[AuditResult] = []
    non_compliant = 0
    for flow in flows:
        source = flow.get("source_region", "")
        destination = flow.get("destination_region", "")
        authorized = bool(flow.get("authorized"))
        is_cross_border = source != destination
        legal_mechanism = flow.get("legal_mechanism", "None") or "None"
        # Cross-border transfers must both be authorized and backed by a recognised legal mechanism.
        has_legal_mechanism = (not is_cross_border) or (legal_mechanism in _VALID_CROSS_BORDER_MECHANISMS)
        passed = authorized and has_legal_mechanism
        status = "PASSED" if passed else "FAILED"
        if not passed:
            non_compliant += 1
        results.append(
            AuditResult(
                check_id=str(flow.get("flow_id", "unknown")),
                status=status,
                details=f"{source}->{destination}, authorized={authorized}, mechanism={legal_mechanism}",
            )
        )

    overall_status = "NON_COMPLIANT" if non_compliant else "COMPLIANT"
    audit_id = "LOC-AUDIT-001"
    framework = "GDPR_DPDP"
    data_state_hash = generate_sha256_hash(json.dumps(flows, sort_keys=True))
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
