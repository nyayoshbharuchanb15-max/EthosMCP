# src/services/localization.py

import json
from typing import List, Dict, Any
from src.models import AuditReport, AuditResult
from src.config import settings

def load_data_flow_map() -> List[Dict[str, Any]]:
    data_flow_file_path = f"{settings.DATA_DIR}/data_flow_map.json"
    try:
        with open(data_flow_file_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []

async def analyze_data_flow() -> AuditReport:
    """Examines infrastructural network boundaries and regional compliance."""
    data_flow_map = load_data_flow_map()
    results = []

    if not data_flow_map:
        results.append(AuditResult(check_id="DATA-FLOW-LOAD", status="FAILED", details="No data flow map found to audit."))
        overall_status = "NON_COMPLIANT"
    else:
        for flow in data_flow_map:
            flow_id = flow.get("flow_id", "UNKNOWN_FLOW")
            source_region = flow.get("source_region")
            destination_region = flow.get("destination_region")
            legal_mechanism = flow.get("legal_mechanism")
            authorized = flow.get("authorized", False)

            if source_region == "EU" and destination_region != "EU" and legal_mechanism != "SCCs":
                results.append(AuditResult(check_id=f"EU-CROSS-BORDER-{flow_id}", status="FAILED", details=f"EU data from {source_region} to {destination_region} without SCCs."))
            else:
                results.append(AuditResult(check_id=f"EU-CROSS-BORDER-{flow_id}", status="PASSED"))

            if source_region == "India" and destination_region != "India":
                results.append(AuditResult(check_id=f"INDIA-SOVEREIGNTY-{flow_id}", status="FAILED", details=f"India data from {source_region} to {destination_region} violates DPDP."))
            else:
                results.append(AuditResult(check_id=f"INDIA-SOVEREIGNTY-{flow_id}", status="PASSED"))

            if not authorized:
                results.append(AuditResult(check_id=f"FLOW-AUTHORIZED-{flow_id}", status="FAILED", details=f"Data flow {flow_id} is not authorized."))
            else:
                results.append(AuditResult(check_id=f"FLOW-AUTHORIZED-{flow_id}", status="PASSED"))

        if any(r.status == "FAILED" for r in results):
            overall_status = "NON_COMPLIANT"
        elif any(r.status == "WARNING" for r in results):
            overall_status = "WARNING"
        else:
            overall_status = "COMPLIANT"

    return AuditReport(
        audit_id="LOC-AUDIT-001",
        framework="GDPR_DPDP",
        results=results,
        overall_status=overall_status,
        query_hash_digest="mock_query_hash_loc",
        response_signature="mock_response_signature_loc",
        data_state_hash="mock_data_state_hash_loc"
    )
