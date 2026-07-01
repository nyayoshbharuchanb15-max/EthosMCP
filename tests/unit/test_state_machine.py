import pytest


class PhaseStatus:
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    PASS = "PASS"
    FAIL = "FAIL"
    BLOCKER = "BLOCKER"


class PipelineStateMachine:
    PHASE_DEPENDENCIES: dict[int, list[int]] = {
        1: [],
        2: [1],
        3: [2],
        4: [3],
        5: [4],
        6: [5],
        7: [6],
        8: [1, 2, 3, 4, 5, 6, 7],
        9: [8],
    }

    def __init__(self):
        self.phases: dict[int, str] = {}
        self.run_certified = False

    def set_phase(self, phase: int, status: str):
        self.phases[phase] = status

    def can_execute(self, phase: int) -> tuple[bool, str]:
        if self.run_certified:
            return False, "CERTIFIED run cannot be modified"
        deps = self.PHASE_DEPENDENCIES.get(phase, [])
        for dep in deps:
            status = self.phases.get(dep, PhaseStatus.PENDING)
            if status != PhaseStatus.PASS:
                return False, f"Phase {dep} must be PASS before phase {phase} can execute. Current: {status}"
        return True, "OK"

    def has_blocker_findings(self) -> bool:
        for phase, status in self.phases.items():
            if status == PhaseStatus.BLOCKER:
                return True
        return False

    def trigger_reaudit(self, changed_components: list[str]) -> dict[int, str]:
        new_phases: dict[int, str] = {}
        for phase in sorted(self.PHASE_DEPENDENCIES.keys()):
            new_phases[phase] = PhaseStatus.PENDING
        return new_phases

    def certify(self):
        self.run_certified = True


class TestStateMachine:

    @pytest.fixture
    def machine(self):
        return PipelineStateMachine()

    def test_phase2_blocked_if_phase1_not_passed(self, machine):
        can, reason = machine.can_execute(2)
        assert not can
        assert "Phase 1" in reason

    def test_phase8_blocked_if_any_previous_phase_not_passed(self, machine):
        for ph in range(1, 8):
            machine.set_phase(ph, PhaseStatus.PASS)
        machine.set_phase(3, PhaseStatus.PENDING)
        can, reason = machine.can_execute(8)
        assert not can
        assert "Phase 3" in reason

    def test_phase8_blocked_if_blocker_finding_exists(self, machine):
        for ph in range(1, 8):
            machine.set_phase(ph, PhaseStatus.PASS)
        machine.set_phase(4, PhaseStatus.BLOCKER)
        can, reason = machine.can_execute(8)
        assert not can

    def test_reaudit_only_marks_dependent_phases_pending(self, machine):
        for ph in range(1, 9):
            machine.set_phase(ph, PhaseStatus.PASS)
        new_phases = machine.trigger_reaudit(["model_endpoint"])
        for ph, status in new_phases.items():
            assert status == PhaseStatus.PENDING

    def test_certified_run_cannot_be_modified(self, machine):
        for ph in range(1, 9):
            machine.set_phase(ph, PhaseStatus.PASS)
        machine.certify()
        can, reason = machine.can_execute(9)
        assert not can
        assert "CERTIFIED" in reason
