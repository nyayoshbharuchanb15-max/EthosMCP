from __future__ import annotations

from typing import Any

from src.models.audit import AuditReport, AuditResult


def get_ropa_records() -> AuditReport:
    return AuditReport(
        audit_id="GOV-AUDIT-001",
        framework="GDPR",
        results=[AuditResult(check_id="ropa", status="PASSED")],
        overall_status="WARNING",
        execution_timestamp="2026-06-23T00:00:00Z",
        query_hash_digest="",
        response_signature="",
        data_state_hash="",
    )
