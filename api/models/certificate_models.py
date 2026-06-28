from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class CertificateInput(BaseModel):
    audit_session_id: str
    weighted_audit_score: Dict[str, Any]
    blocker_fail_detected: bool

class CertificateResult(BaseModel):
    vc_json: Dict[str, Any]
    pdf_base64: str
    issued_at: str
    explanation: str
    regulatory_basis: List[str]

class FailNotice(BaseModel):
    fail_notice_id: str
    audit_session_id: str
    reason: str
    details: str
    issued_at: str
    explanation: str
    regulatory_basis: List[str]
