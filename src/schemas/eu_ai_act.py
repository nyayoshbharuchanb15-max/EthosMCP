# src/schemas/eu_ai_act.py

from typing import List, Optional
from pydantic import BaseModel, Field

class EuAiActTrainingDataCheck(BaseModel):
    model_id: str = Field(..., description="Identifier for the AI model")
    data_lineage_documented: bool = Field(..., description="Whether training data lineage is documented")
    bias_logging_enabled: bool = Field(..., description="Whether model bias logging is enabled")
    data_quality_score: float = Field(..., description="Score indicating the quality of training data (e.g., 0-1)")

class EuAiActRiskGovernanceCheck(BaseModel):
    system_id: str = Field(..., description="Identifier for the AI system")
    iso_42001_aligned: bool = Field(..., description="Whether the AI system is aligned with ISO/IEC 42001")
    risk_assessment_conducted: bool = Field(..., description="Whether a risk assessment has been conducted")
    human_oversight_mechanisms: List[str] = Field(default_factory=list, description="List of human oversight mechanisms in place")
