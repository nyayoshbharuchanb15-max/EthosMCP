# src/services/sovereignty.py

import json
from typing import List, Dict, Any
from src.models import AuditReport, AuditResult
from src.config import settings

def load_consent_registry() -> List[Dict[str, Any]]:
    consent_file_path = f"{settings.DATA_DIR}/consent_registry.json"
    try:
        with open(consent_file_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []

async def query_consent_registry() -> AuditReport:
    """Audits the structural integrity of the front-end consent lifecycle."""
    consent_data_list = load_consent_registry()
    results = []

    if not consent_data_list:
        results.append(AuditResult(check_id="CONSENT-DATA-LOAD", status="FAILED", details="No consent registry data found to audit."))
        overall_status = "NON_COMPLIANT"
    else:
        for consent_data in consent_data_list:
            user_id = consent_data.get("user_id", "UNKNOWN_USER")
            consent_id = consent_data.get("consent_id", "UNKNOWN_CONSENT")

            if not consent_data.get("explicit_consent"):
                results.append(AuditResult(check_id=f"EXPLICIT-CONSENT-{consent_id}", status="FAILED", details=f"User {user_id}: Explicit consent not recorded."))
            else:
                results.append(AuditResult(check_id=f"EXPLICIT-CONSENT-{consent_id}", status="PASSED"))

            withdrawal_friction_score = consent_data.get("withdrawal_friction_score", 0)
            if withdrawal_friction_score > 3:
                results.append(AuditResult(check_id=f"WITHDRAWAL-FRICTION-{consent_id}", status="FAILED", details=f"User {user_id}: High withdrawal friction score."))
            else:
                results.append(AuditResult(check_id=f"WITHDRAWAL-FRICTION-{consent_id}", status="PASSED"))

        if any(r.status == "FAILED" for r in results):
            overall_status = "NON_COMPLIANT"
        elif any(r.status == "WARNING" for r in results):
            overall_status = "WARNING"
        else:
            overall_status = "COMPLIANT"

    return AuditReport(
        audit_id="SOV-AUDIT-001",
        framework="GDPR_DPDP",
        results=results,
        overall_status=overall_status,
        query_hash_digest="mock_query_hash_sov_consent",
        response_signature="mock_response_signature_sov_consent",
        data_state_hash="mock_data_state_hash_sov_consent"
    )

async def simulate_dsar_workflow(dsar_request: Dict[str, Any]) -> AuditReport:
    """Evaluates system capacity to fulfill individual access and erasure requests."""
    results = []
    user_id = dsar_request.get("user_id", "UNKNOWN_USER")
    request_type = dsar_request.get("request_type", "UNKNOWN_TYPE")
    erasure_latency_days = dsar_request.get("erasure_latency_days", 0)

    if request_type == "erasure" and erasure_latency_days > 30:
        results.append(AuditResult(check_id=f"DSAR-ERASURE-LATENCY-{user_id}", status="FAILED", details=f"User {user_id}: Erasure latency exceeds 30 days."))
    else:
        results.append(AuditResult(check_id=f"DSAR-ERASURE-LATENCY-{user_id}", status="PASSED"))

    overall_status = "COMPLIANT" if all(r.status == "PASSED" for r in results) else "NON_COMPLIANT"

    return AuditReport(
        audit_id="DSAR-SIM-001",
        framework="GDPR_DPDP",
        results=results,
        overall_status=overall_status,
        query_hash_digest="mock_query_hash_sov_dsar",
        response_signature="mock_response_signature_sov_dsar",
        data_state_hash="mock_data_state_hash_sov_dsar"
    )
