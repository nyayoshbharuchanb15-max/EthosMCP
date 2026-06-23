from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class AuditResult:
    check_id: str
    status: str
    details: str | None = None

@dataclass(frozen=True)
class AuditReport:
    audit_id: str
    framework: str
    results: list[AuditResult]
    overall_status: str
    execution_timestamp: str
    query_hash_digest: str
    response_signature: str
    data_state_hash: str
