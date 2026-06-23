from __future__ import annotations

import json
from datetime import datetime, timezone

from src.models.audit import AuditReport, AuditResult
from src.tools import load_metadata_records
from src.utils.crypto import generate_hmac_signature, generate_sha256_hash


async def audit_encryption_coverage() -> AuditReport:
    systems = load_metadata_records("security_config.json")
    results: list[AuditResult] = []
    non_compliant = 0
    for system in systems:
        at_rest = bool(system.get("at_rest_aes256"))
        in_transit = bool(system.get("in_transit_tls13"))
        breach_detection = bool(system.get("breach_detection_configured"))
        # All third-party processors must have a signed Data Processing Agreement (GDPR Art. 28).
        dpa_parties = system.get("dpa_signed_third_parties", [])
        all_dpa_signed = all(bool(p.get("dpa_signed")) for p in dpa_parties) if dpa_parties else True
        passed = at_rest and in_transit and breach_detection and all_dpa_signed
        if not passed:
            non_compliant += 1
        results.append(
            AuditResult(
                check_id=str(system.get("system_id", "unknown")),
                status="PASSED" if passed else "FAILED",
                details=(
                    f"at_rest={at_rest}, in_transit={in_transit}, "
                    f"breach_detection={breach_detection}, all_dpa_signed={all_dpa_signed}"
                ),
            )
        )

    overall_status = "NON_COMPLIANT" if non_compliant else "COMPLIANT"
    audit_id = "SEC-AUDIT-001"
    framework = "ISO42001_GDPR"
    data_state_hash = generate_sha256_hash(json.dumps(systems, sort_keys=True))
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
