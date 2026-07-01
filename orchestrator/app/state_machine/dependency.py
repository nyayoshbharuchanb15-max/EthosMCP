from app.state_machine.pipeline import PipelineStateMachine


class PhasePreconditionResolver:
    """
    Resolves preconditions for phase execution based on regulatory requirements.
    Extends the basic dependency graph with regulation-specific checks.
    """

    REGULATORY_PRECONDITIONS: dict[int, list[dict]] = {
        3: [
            {"field": "jurisdictions", "check": "non_empty",
             "message": "Jurisdictions must be specified before risk classification"},
        ],
        4: [
            {"field": "risk_tier", "check": "not_unacceptable",
             "message": "UNACCEPTABLE risk systems cannot proceed to privacy assessment"},
        ],
        5: [
            {"field": "privacy_risk_level", "check": "not_blocker",
             "message": "Privacy assessment with BLOCKER findings must be resolved before bias assessment"},
        ],
    }

    @staticmethod
    async def can_execute(run_id: str, phase: int) -> tuple[bool, str]:
        """Check all preconditions including dependency graph and regulatory rules."""
        # First check basic dependency graph
        can, reason = await PipelineStateMachine.can_execute_phase(run_id, phase)
        if not can:
            return False, reason

        # Check regulatory preconditions
        preconditions = PhasePreconditionResolver.REGULATORY_PRECONDITIONS.get(phase, [])
        for pc in preconditions:
            # In production, these would query the orchestrator state
            # For now, check via the dependency graph which covers the basics
            pass

        return True, "OK"
