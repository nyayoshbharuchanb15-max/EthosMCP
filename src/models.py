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
    ropa_id: str = Field(..., description="Unique identifier for the ROPA entry")
    processing_activity: str = Field(..., description="Description of the data processing activity")
    legal_basis: str = Field(..., description="Legal basis for processing (e.g., Consent, Contract, Legal Obligation)")
    data_categories: List[str] = Field(..., description="Categories of personal data processed")
    purpose: str = Field(..., description="Purpose of the data processing")
    department_owner: str = Field(..., description="Department responsible for the processing activity")
    data_subject_categories: List[str] = Field(..., description="Categories of data subjects")
    recipients: List[str] = Field(..., description="Recipients of the personal data")
    data_retention_period: str = Field(..., description="Period for which the personal data will be stored")
    security_measures: str = Field(..., description="Description of technical and organizational security measures")
