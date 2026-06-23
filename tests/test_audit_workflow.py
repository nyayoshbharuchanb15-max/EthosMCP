import pytest

from src.workflow import run_audit_workflow


@pytest.mark.asyncio
async def test_run_audit_workflow_returns_structured_report():
    report = await run_audit_workflow()
    assert report["protocol"] == "ethosmcp_four_phase_v1"
    assert len(report["phase_outcomes"]) == 4
    assert [phase["phase_id"] for phase in report["phase_outcomes"]] == [
        "phase_1_governance",
        "phase_2_localization",
        "phase_3_sovereignty",
        "phase_4_security",
    ]
    phase_3 = report["phase_outcomes"][2]
    assert [step["tool_name"] for step in phase_3["step_outcomes"]] == [
        "query_consent_registry",
        "simulate_dsar_workflow",
    ]
    assert len(report["audit_trail"]) == 4


@pytest.mark.asyncio
async def test_run_audit_workflow_can_stop_after_failure():
    report = await run_audit_workflow({"continue_on_failure": False})
    statuses = [phase["status"] for phase in report["phase_outcomes"]]
    assert statuses[:2] == ["WARNING", "FAILED"]
    assert statuses[2:] == ["SKIPPED", "SKIPPED"]
