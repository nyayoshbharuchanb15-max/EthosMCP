from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass
from hashlib import sha256
from json import dumps
from typing import Any, Awaitable, Callable, Literal, cast

from src.models.workflow import (
    AuditTrailEntry,
    AuditWorkflowReport,
    AuditWorkflowRequest,
    PhaseOutcome,
    PhaseStepOutcome,
)
from src.services import governance, localization, security, sovereignty

StepRunner = Callable[[AuditWorkflowRequest], Awaitable[Any]]
HASH_PREFIX_LENGTH = 16


@dataclass(frozen=True)
class PhaseDefinition:
    phase_id: str
    phase_name: str
    expected_token: str
    steps: tuple[tuple[str, StepRunner], ...]


def _overall_to_phase_status(overall_status: str) -> str:
    normalized = overall_status.upper()
    if normalized in {"PASSED", "COMPLIANT"}:
        return "PASSED"
    if normalized == "WARNING":
        return "WARNING"
    if normalized in {"FAILED", "NON_COMPLIANT"}:
        return "FAILED"
    return "ERROR"


def _stable_serialize(value: Any) -> str:
    return dumps(value, sort_keys=True, separators=(",", ":"))


def _build_phase_token(phase_id: str, step_outcomes: list[PhaseStepOutcome]) -> str:
    digest_source = []
    for step in step_outcomes:
        digest_source.append(
            {
                "tool_name": step.tool_name,
                "report": step.report,
                "error": step.error,
            }
        )
    digest = sha256(_stable_serialize({"phase_id": phase_id, "steps": digest_source}).encode("utf-8")).hexdigest()
    return f"{phase_id}:{digest[:HASH_PREFIX_LENGTH]}"


PHASES: tuple[PhaseDefinition, ...] = (
    PhaseDefinition(
        phase_id="phase_1_governance",
        phase_name="Governance & ROPA Alignment",
        expected_token="governance_baseline_v1",
        steps=(("audit_ropa_alignment", lambda _: governance.audit_ropa_alignment()),),
    ),
    PhaseDefinition(
        phase_id="phase_2_localization",
        phase_name="Data Localization & Cross-Border Mapping",
        expected_token="localization_baseline_v1",
        steps=(("analyze_data_flow", lambda _: localization.analyze_data_flow()),),
    ),
    PhaseDefinition(
        phase_id="phase_3_sovereignty",
        phase_name="Consent Lifecycle & Individual Rights",
        expected_token="rights_baseline_v1",
        steps=(
            ("query_consent_registry", lambda _: sovereignty.query_consent_registry()),
            ("simulate_dsar_workflow", lambda request: sovereignty.simulate_dsar_workflow(request.dsar_request)),
        ),
    ),
    PhaseDefinition(
        phase_id="phase_4_security",
        phase_name="Technical Controls & Security Posture",
        expected_token="security_posture_v1",
        steps=(("audit_encryption_coverage", lambda _: security.audit_encryption_coverage()),),
    ),
)


async def run_audit_workflow(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    request = AuditWorkflowRequest.model_validate(payload or {})
    phase_outcomes: list[PhaseOutcome] = []
    audit_trail: list[AuditTrailEntry] = []
    issued_tokens: list[str] = []
    prerequisite_token: str | None = None
    block_remaining = False

    for index, phase in enumerate(PHASES, start=1):
        incoming_token = prerequisite_token
        gate_status: Literal["READY", "MISSING_PREREQUISITE_TOKEN"] = (
            "READY" if index == 1 or incoming_token else "MISSING_PREREQUISITE_TOKEN"
        )
        if block_remaining:
            phase_outcome = PhaseOutcome(
                phase_id=phase.phase_id,
                phase_name=phase.phase_name,
                expected_token=phase.expected_token,
                prerequisite_token=incoming_token,
                gate_status=gate_status,
                status="SKIPPED",
                issued_token=None,
                step_outcomes=[],
            )
        else:
            step_outcomes: list[PhaseStepOutcome] = []
            phase_status: Literal["PASSED", "WARNING", "FAILED", "ERROR", "SKIPPED"] = "PASSED"
            for tool_name, step_runner in phase.steps:
                try:
                    result = await step_runner(request)
                    if is_dataclass(result) and not isinstance(result, type):
                        report = asdict(result)
                    else:
                        report = cast(dict[str, Any], result)
                    step_outcomes.append(PhaseStepOutcome(tool_name=tool_name, report=report))
                    status = _overall_to_phase_status(str(report.get("overall_status", "ERROR")))
                    if status == "ERROR":
                        phase_status = "ERROR"
                    elif status == "FAILED" and phase_status not in {"ERROR"}:
                        phase_status = "FAILED"
                    elif status == "WARNING" and phase_status == "PASSED":
                        phase_status = "WARNING"
                except Exception as exc:  # pragma: no cover - defensive path
                    step_outcomes.append(
                        PhaseStepOutcome(tool_name=tool_name, error=f"{type(exc).__name__}: {exc}")
                    )
                    phase_status = "ERROR"

            issued_token = None
            if phase_status in {"PASSED", "WARNING"}:
                issued_token = _build_phase_token(phase.phase_id, step_outcomes)
                prerequisite_token = issued_token
                issued_tokens.append(issued_token)
            elif not request.continue_on_failure:
                block_remaining = True

            phase_outcome = PhaseOutcome(
                phase_id=phase.phase_id,
                phase_name=phase.phase_name,
                expected_token=phase.expected_token,
                prerequisite_token=incoming_token if index > 1 else None,
                gate_status=gate_status,
                status=phase_status,
                issued_token=issued_token,
                step_outcomes=step_outcomes,
            )

        phase_outcomes.append(phase_outcome)
        audit_trail.append(
            AuditTrailEntry(
                sequence=index,
                phase_id=phase.phase_id,
                status=phase_outcome.status,
                issued_token=phase_outcome.issued_token,
                prerequisite_token=phase_outcome.prerequisite_token,
                gate_status=phase_outcome.gate_status,
            )
        )

    status_values = {phase.status for phase in phase_outcomes}
    # Any failed/error/skipped phase marks the workflow as failed so the final report is explicit.
    overall_status: Literal["PASSED", "FAILED"] = (
        "PASSED" if status_values.issubset({"PASSED", "WARNING"}) else "FAILED"
    )
    workflow_id = sha256(
        _stable_serialize(
            {
                "continue_on_failure": request.continue_on_failure,
                "dsar_request": request.dsar_request,
                "phases": [phase.phase_id for phase in PHASES],
            }
        ).encode("utf-8")
    ).hexdigest()[:HASH_PREFIX_LENGTH]
    workflow_report = AuditWorkflowReport(
        workflow_id=f"ETHOS-{workflow_id}",
        overall_status=overall_status,
        phase_outcomes=phase_outcomes,
        issued_tokens=issued_tokens,
        audit_trail=audit_trail,
    )
    return workflow_report.model_dump()
