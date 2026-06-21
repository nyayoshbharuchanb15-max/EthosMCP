# src/services/security.py

import json
from typing import List, Dict, Any
from src.models import AuditReport, AuditResult
from src.config import settings

def load_security_config() -> List[Dict[str, Any]]:
    security_file_path = f"{settings.DATA_DIR}/security_config.json"
    try:
        with open(security_file_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []

async def audit_encryption_coverage() -> AuditReport:
    """Verifies encryption coverage for data at rest and in transit."""
    security_configs = load_security_config()
    results = []

    if not security_configs:
        results.append(AuditResult(check_id="SECURITY-CONFIG-LOAD", status="FAILED", details="No security configuration found to audit."))
        overall_status = "NON_COMPLIANT"
    else:
        for config in security_configs:
            system_id = config.get("system_id", "UNKNOWN_SYSTEM")

            if not config.get("at_rest_aes256"):
                results.append(AuditResult(check_id=f"ENCRYPTION-AT-REST-{system_id}", status="FAILED", details=f"System {system_id}: AES-256 encryption at rest not confirmed."))
            else:
                results.append(AuditResult(check_id=f"ENCRYPTION-AT-REST-{system_id}", status="PASSED"))

            if not config.get("in_transit_tls13"):
                results.append(AuditResult(check_id=f"ENCRYPTION-IN-TRANSIT-{system_id}", status="FAILED", details=f"System {system_id}: TLS 1.3 or higher not confirmed."))
            else:
                results.append(AuditResult(check_id=f"ENCRYPTION-IN-TRANSIT-{system_id}", status="PASSED"))

            if not config.get("breach_detection_configured"):
                results.append(AuditResult(check_id=f"BREACH-DETECTION-{system_id}", status="WARNING", details=f"System {system_id}: Breach detection workflows not confirmed."))
            else:
                results.append(AuditResult(check_id=f"BREACH-DETECTION-{system_id}", status="PASSED"))

            for dpa in config.get("dpa_signed_third_parties", []):
                processor_id = dpa.get("processor_id", "UNKNOWN_PROCESSOR")
                if not dpa.get("dpa_signed"):
                    results.append(AuditResult(check_id=f"PROCESSOR-DPA-{system_id}-{processor_id}", status="FAILED", details=f"System {system_id}, Processor {processor_id}: DPA not signed."))
                else:
                    results.append(AuditResult(check_id=f"PROCESSOR-DPA-{system_id}-{processor_id}", status="PASSED"))

        if any(r.status == "FAILED" for r in results):
            overall_status = "NON_COMPLIANT"
        elif any(r.status == "WARNING" for r in results):
            overall_status = "WARNING"
        else:
            overall_status = "COMPLIANT"

    return AuditReport(
        audit_id="SEC-AUDIT-001",
        framework="ISO_IEC_42001",
        results=results,
        overall_status=overall_status,
        query_hash_digest="mock_query_hash_sec",
        response_signature="mock_response_signature_sec",
        data_state_hash="mock_data_state_hash_sec"
    )
