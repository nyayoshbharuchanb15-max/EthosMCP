from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

DEFAULT_DSAR_REQUEST: dict[str, Any] = {
    "user_id": "synthetic_user_001",
    "request_type": "erasure",
    "erasure_latency_days": 20,
}


class AuditWorkflowRequest(BaseModel):
    continue_on_failure: bool = Field(
        default=True,
        description="Continue executing later phases even after failures.",
    )
    dsar_request: dict[str, Any] = Field(
        default_factory=lambda: DEFAULT_DSAR_REQUEST.copy()
    )


class PhaseStepOutcome(BaseModel):
    tool_name: str
    report: dict[str, Any] | None = None
    error: str | None = None


class PhaseOutcome(BaseModel):
    phase_id: str
    phase_name: str
    expected_token: str
    prerequisite_token: str | None = None
    gate_status: Literal["READY", "MISSING_PREREQUISITE_TOKEN"]
    status: Literal["PASSED", "WARNING", "FAILED", "ERROR", "SKIPPED"]
    issued_token: str | None = None
    step_outcomes: list[PhaseStepOutcome]


class AuditTrailEntry(BaseModel):
    sequence: int
    phase_id: str
    status: str
    issued_token: str | None = None
    prerequisite_token: str | None = None
    gate_status: str


class AuditWorkflowReport(BaseModel):
    workflow_id: str
    protocol: str = "ethosmcp_four_phase_v1"
    overall_status: Literal["PASSED", "FAILED"]
    phase_outcomes: list[PhaseOutcome]
    issued_tokens: list[str]
    audit_trail: list[AuditTrailEntry]
