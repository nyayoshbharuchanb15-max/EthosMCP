from __future__ import annotations

import json
from datetime import datetime, timezone

from src.models.audit import AuditReport, AuditResult
from src.tools import load_metadata_records
from src.utils.crypto import generate_hmac_signature, generate_sha256_hash

MIN_PURPOSE_DESCRIPTION_LENGTH = 10


async def get_ropa_records() -> AuditReport:
    records = load_metadata_records("ropa_records.json")
    coverage = len(records)
    overall_status = "PASSED" if coverage > 0 else "WARNING"
    audit_id = "GOV-ROPA-001"
    framework = "GDPR"
    execution_timestamp = datetime.now(timezone.utc).isoformat()
    data_state_hash = generate_sha256_hash(json.dumps(records, sort_keys=True))
    query_hash_digest = generate_sha256_hash(f"{audit_id}:{framework}")
    response_signature = generate_hmac_signature(
        f"{audit_id}:{framework}:{overall_status}:coverage={coverage}"
    )
    return AuditReport(
        audit_id=audit_id,
        framework=framework,
        results=[AuditResult(check_id="ropa_records_count", status="COMPLIANT", details=str(coverage))],
        overall_status=overall_status,
        execution_timestamp=execution_timestamp,
        query_hash_digest=query_hash_digest,
        response_signature=response_signature,
        data_state_hash=data_state_hash,
    )


async def audit_ropa_alignment() -> AuditReport:
    records = load_metadata_records("ropa_records.json")
    results: list[AuditResult] = []
    warning_count = 0
    for record in records:
        purpose = record.get("purpose", "")
        legal_basis = record.get("legal_basis", "")
        data_categories = record.get("data_categories", [])
        # Purpose-limitation: description must meet the minimum length floor.
        purpose_ok = len(purpose) >= MIN_PURPOSE_DESCRIPTION_LENGTH
        # Legal basis and data categories must be explicitly documented (GDPR Art. 30).
        legal_basis_ok = bool(legal_basis)
        data_categories_ok = bool(data_categories)
        passed = purpose_ok and legal_basis_ok and data_categories_ok
        status = "PASSED" if passed else "WARNING"
        if not passed:
            warning_count += 1
        results.append(
            AuditResult(
                check_id=str(record.get("ropa_id", "unknown")),
                status=status,
                details=f"purpose={purpose}, legal_basis={legal_basis}, data_categories_present={data_categories_ok}",
            )
        )

    overall_status = "WARNING" if warning_count else "PASSED"
    audit_id = "GOV-AUDIT-001"
    framework = "GDPR"
    data_state_hash = generate_sha256_hash(json.dumps(records, sort_keys=True))
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
