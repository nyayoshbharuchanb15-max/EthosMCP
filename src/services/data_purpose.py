from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from src.models.audit import AuditReport, AuditResult
from src.tools import load_metadata_records
from src.utils.crypto import generate_hmac_signature, generate_sha256_hash


async def verify_data_purpose(payload: dict[str, Any]) -> AuditReport:
    dataset_id = str(payload.get("dataset_id", ""))
    requested_purpose = str(payload.get("requested_purpose", ""))

    registry = load_metadata_records("dataset_purpose_registry.json")
    dataset = next((r for r in registry if r.get("dataset_id") == dataset_id), None)

    audit_id = "PURPOSE-AUDIT-001"
    framework = "EU_AI_ACT_GDPR"

    if dataset is None:
        result = AuditResult(
            check_id=f"purpose_check:{dataset_id}",
            status="FAILED",
            details=f"dataset_id={dataset_id}, requested_purpose={requested_purpose}, reason=unknown_dataset",
        )
        overall_status = "NON_COMPLIANT"
    else:
        allowed_purposes: list[str] = dataset.get("allowed_purposes", [])
        prohibited_purposes: list[str] = dataset.get("prohibited_purposes", [])
        is_allowed = requested_purpose in allowed_purposes
        is_prohibited = requested_purpose in prohibited_purposes
        # A purpose is compliant only when it is explicitly allowed and not prohibited.
        compliant = is_allowed and not is_prohibited
        result = AuditResult(
            check_id=f"purpose_check:{dataset_id}",
            status="PASSED" if compliant else "FAILED",
            details=(
                f"dataset_id={dataset_id}, requested_purpose={requested_purpose}, "
                f"allowed={is_allowed}, prohibited={is_prohibited}"
            ),
        )
        overall_status = "COMPLIANT" if compliant else "NON_COMPLIANT"

    data_state_hash = generate_sha256_hash(json.dumps(registry, sort_keys=True))
    query_hash_digest = generate_sha256_hash(f"{audit_id}:{framework}:{dataset_id}:{requested_purpose}")
    response_signature = generate_hmac_signature(
        f"{audit_id}:{framework}:{overall_status}:{dataset_id}:{requested_purpose}"
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
