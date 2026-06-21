# src/schemas/dpdp_parameters.py

from typing import List, Optional
from pydantic import BaseModel, Field

class DpdpNoticeCheck(BaseModel):
    system_id: str = Field(..., description="Identifier for the system being audited")
    expected_languages: List[str] = Field(..., description="List of expected languages for notices")
    notice_accessibility_score: int = Field(..., description="Score indicating accessibility of notices (e.g., 1-5)")

class DpdpConsentCheck(BaseModel):
    user_id: str = Field(..., description="Identifier for the user")
    consent_granularity_required: bool = Field(..., description="Whether granular consent is required")
    consent_withdrawal_friction_score: int = Field(..., description="Score indicating friction in consent withdrawal (e.g., 1-5)")

class DpdpErasureCheck(BaseModel):
    data_subject_id: str = Field(..., description="Identifier for the data subject")
    erasure_propagation_status: str = Field(..., description="Status of erasure propagation (e.g., complete, partial, failed)")
