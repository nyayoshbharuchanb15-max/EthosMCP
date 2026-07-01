from pydantic import BaseModel
from typing import Optional, Literal
from uuid import UUID


class AuditRunResponse(BaseModel):
    run_id: UUID
    system_id: UUID
    system_name: str
    system_version: str
    status: str
    created_at: str


class PhaseResultResponse(BaseModel):
    result_id: UUID
    run_id: UUID
    phase_number: int
    status: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    artifact_hash: Optional[str] = None


class FindingResponse(BaseModel):
    finding_id: UUID
    severity: str
    regulation: str
    article: str
    description: str
    remediation: str


class BlockerFinding(BaseModel):
    finding_id: UUID
    severity: Literal["BLOCKER"]
    regulation: str
    article: str
    description: str


class AuditStatusResponse(BaseModel):
    run_id: UUID
    status: str
    phases: dict[int, str]
    blocker_findings: list[BlockerFinding]
    artifacts: list[dict]
