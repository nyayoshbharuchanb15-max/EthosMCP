# src/services/governance.py

import json
from typing import List
from src.models import AuditReport, AuditResult, RopaEntry
from src.config import settings

def load_ropa_records() -> List[RopaEntry]:
    ropa_file_path = f"{settings.DATA_DIR}/ropa_records.json"
    try:
        with open(ropa_file_path, "r") as f:
            data = json.load(f)
            return [RopaEntry(**item) for item in data]
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []

async def get_ropa_records() -> List[RopaEntry]:
    """Accesses foundational data classification mapping tables."""
    return load_ropa_records()

async def audit_ropa_alignment() -> AuditReport:
    """Verifies ROPA alignment and purpose limitation."""
    ropa_data = load_ropa_records()
    results = []

    if not ropa_data:
        results.append(AuditResult(check_id="ROPA-DATA-LOAD", status="FAILED", details="No ROPA data found to audit."))
        overall_status = "NON_COMPLIANT"
    else:
        for entry in ropa_data:
            if not entry.legal_basis:
                results.append(AuditResult(check_id=f"ROPA-LEGAL-BASIS-{entry.ropa_id}", status="FAILED", details="Missing legal basis."))
            else:
                results.append(AuditResult(check_id=f"ROPA-LEGAL-BASIS-{entry.ropa_id}", status="PASSED"))

            if len(entry.purpose) < 10:
                results.append(AuditResult(check_id=f"ROPA-PURPOSE-MIN-{entry.ropa_id}", status="WARNING", details="Purpose description might be too vague."))
            else:
                results.append(AuditResult(check_id=f"ROPA-PURPOSE-MIN-{entry.ropa_id}", status="PASSED"))

            if not entry.department_owner:
                results.append(AuditResult(check_id=f"ROPA-OWNERSHIP-{entry.ropa_id}", status="FAILED", details="Missing department owner."))
            else:
                results.append(AuditResult(check_id=f"ROPA-OWNERSHIP-{entry.ropa_id}", status="PASSED"))

        if any(r.status == "FAILED" for r in results):
            overall_status = "NON_COMPLIANT"
        elif any(r.status == "WARNING" for r in results):
            overall_status = "WARNING"
        else:
            overall_status = "COMPLIANT"

    return AuditReport(
        audit_id="GOV-AUDIT-001",
        framework="GDPR",
        results=results,
        overall_status=overall_status,
        query_hash_digest="mock_query_hash_gov",
        response_signature="mock_response_signature_gov",
        data_state_hash="mock_data_state_hash_gov"
    )
