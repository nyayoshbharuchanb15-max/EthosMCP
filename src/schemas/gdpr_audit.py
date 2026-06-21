# src/schemas/gdpr_audit.py

from typing import List, Optional
from pydantic import BaseModel, Field

class GdprRopaCheck(BaseModel):
    ropa_id: str = Field(..., description="ROPA entry ID to check")
    expected_legal_basis: str
    # Add more GDPR-specific ROPA check parameters

class GdprDsarSimulation(BaseModel):
    data_subject_id: str
    request_type: str = Field(..., description="e.g., access, erasure, rectification")
    expected_latency_days: int = Field(..., description="Expected days for fulfillment")
    # Add more DSAR simulation parameters
