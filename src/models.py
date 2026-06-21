# src/models.py

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

class AuditResult(BaseModel):
    check_id: str = Field(..., description="Unique identifier for the audit check")
    status: str = Field(..., description="Status of the audit check (e.g., PASSED, FAILED, WARNING)")
    details: Optional[str] = Field(None, description="Detailed message or explanation")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="UTC timestamp of the audit")

class AuditReport(BaseModel):
    audit_id: str = Field(..., description="Unique identifier for the overall audit")
    framework: str = Field(..., description="Compliance framework (e.g., GDPR, DPDP, EU_AI_ACT)")
    results: List[AuditResult]
    overall_status: str = Field(..., description="Overall status of the audit (e.g., COMPLIANT, NON_COMPLIANT)")
    execution_timestamp: datetime = Field(default_factory=datetime.utcnow, description="UTC timestamp of the audit report generation")
    query_hash_digest: str = Field(..., description="SHA256 hash of the original audit query")
    response_signature: str = Field(..., description="HMAC-SHA256 signature of the audit response")
    data_state_hash: str = Field(..., description="Hash representing the state of audited data at the time of audit")

# Example for a ROPA entry
class RopaEntry(BaseModel):
    ropa_id: str
    processing_activity: str
    legal_basis: str
    data_categories: List[str]
    purpose: str
    department_owner: str
    # Add other ROPA-specific fields
