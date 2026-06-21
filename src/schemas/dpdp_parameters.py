# src/schemas/dpdp_parameters.py

from typing import List, Optional
from pydantic import BaseModel, Field

class DpdpNoticeCheck(BaseModel):
    system_id: str
    expected_languages: List[str]
    # Add more DPDP-specific notice check parameters

class DpdpConsentCheck(BaseModel):
    user_id: str
    consent_granularity_required: bool
    # Add more DPDP-specific consent check parameters
