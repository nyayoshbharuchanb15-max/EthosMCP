from models.audit_models import HumanOversightInput, OversightResult

class OversightVerifierService:
    def verify(self, input_data: HumanOversightInput) -> OversightResult:
        """
        Verifies human oversight compliance per EU AI Act Art. 14.
        """
        # Critical Check: Kill-switch and Override
        if not input_data.has_kill_switch or not input_data.override_mechanism:
            return OversightResult(
                result="BLOCKER_FAIL",
                has_kill_switch=input_data.has_kill_switch,
                override_capability=input_data.override_mechanism,
                compliance_status="Non-Compliant",
                explanation="BLOCKER_FAIL: The system lacks a functional kill-switch or override mechanism as required by EU AI Act Art. 14(4). Human operators must be able to interrupt the system at any time.",
                regulatory_basis=["EU AI Act Art. 14", "EU AI Act Art. 14(4)"]
            )
            
        if not input_data.monitoring_capability:
             return OversightResult(
                result="PASS",
                has_kill_switch=True,
                override_capability=True,
                compliance_status="Partial-Compliance",
                explanation="The system has emergency controls but lacks real-time human monitoring interfaces. Recommended improvement for full Art. 14 compliance.",
                regulatory_basis=["EU AI Act Art. 14"]
            )

        return OversightResult(
            result="PASS",
            has_kill_switch=True,
            override_capability=True,
            compliance_status="Compliant",
            explanation="The system implements effective human oversight measures, including a functional kill-switch and override capabilities, satisfying EU AI Act Art. 14.",
            regulatory_basis=["EU AI Act Art. 14", "EU AI Act Art. 14(4)"]
        )
