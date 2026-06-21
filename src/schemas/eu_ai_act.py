# src/schemas/eu_ai_act.py

from typing import List, Optional
from pydantic import BaseModel, Field

class EuAiActTrainingDataCheck(BaseModel):
    model_id: str
    data_lineage_documented: bool
    bias_logging_enabled: bool
    # Add more EU AI Act-specific training data check parameters

class EuAiActRiskGovernanceCheck(BaseModel):
    system_id: str
    iso_42001_aligned: bool
    # Add more EU AI Act-specific risk governance parameters
