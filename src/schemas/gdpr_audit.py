# src/schemas/gdpr_audit.py

from typing import List, Optional
from pydantic import BaseModel, Field

class GdprRopaCheck(BaseModel):
    ropa_id: str = Field(..., description="ROPA entry ID to check")
    expected_legal_basis: str = Field(..., description="Expected legal basis for the processing activity")
    expected_purpose_keywords: List[str] = Field(default_factory=list, description="Keywords to check in the purpose description")

class GdprDsarSimulation(BaseModel):
    data_subject_id: str = Field(..., description="Identifier for the data subject")
    request_type: str = Field(..., description="Type of DSAR request (e.g., access, erasure, rectification)")
    expected_latency_days: int = Field(..., description="Expected days for fulfillment of the DSAR request")

class GdprCrossBorderTransferCheck(BaseModel):
    flow_id: str = Field(..., description="Identifier for the data flow")
    source_region: str = Field(..., description="Source region of the data (e.g., EU)")
    destination_region: str = Field(..., description="Destination region of the data (e.g., US)")
    legal_mechanism: Optional[str] = Field(None, description="Legal mechanism for transfer (e.g., SCCs)")
