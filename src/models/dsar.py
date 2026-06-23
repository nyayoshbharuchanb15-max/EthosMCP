from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

class RequestType(str, Enum):
    access = "access"
    erasure = "erasure"
    rectification = "rectification"
    portability = "portability"
    restriction = "restriction"

@dataclass(frozen=True)
class DsarWorkflow:
    subject_identifier_hash: str
    request_type: RequestType
    system_layers: list[str]
    propagation_status: dict[str, str]
    sla_deadline_days: int
    simulation_mode: bool = True
