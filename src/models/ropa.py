from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, Field

class LegalBasis(str, Enum):
    consent = "consent"
    contract = "contract"
    legal_obligation = "legal_obligation"
    vital_interests = "vital_interests"
    public_task = "public_task"
    legitimate_interests = "legitimate_interests"

class ControllerRole(str, Enum):
    parent = "parent"
    subsidiary = "subsidiary"
    joint_controller = "joint_controller"

class RopaRecord(BaseModel):
    processing_activity_id: str = Field(..., pattern=r"^[a-zA-Z0-9_-]{3,64}$")
    controller_entity: str
    controller_role: ControllerRole
    legal_basis: LegalBasis
    data_categories: list[str]
    data_subject_categories: list[str]
    retention_period_days: int
    geographic_scope: list[str]
    third_party_processors: list[str] = []
    ai_system_classification: str
    purpose_limitation_hash: str
