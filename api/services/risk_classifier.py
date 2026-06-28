from models.audit_models import RiskClassificationInput, RiskTierResult, RiskTier

class RiskClassifierService:
    def classify(self, input_data: RiskClassificationInput) -> RiskTierResult:
        """
        Implements EU AI Act risk classification logic per Art. 9.
        """
        # Prohibited AI Practices (Art. 5)
        if "biometric mass surveillance" in input_data.use_case.lower() or \
           "social scoring" in input_data.use_case.lower() or \
           input_data.processes_biometric_data and input_data.autonomous_decision:
            return RiskTierResult(
                tier=RiskTier.PROHIBITED,
                blocking=True,
                explanation="The system falls under Prohibited AI practices (EU AI Act Art. 5) due to use of biometric data for mass surveillance or social scoring.",
                regulatory_basis=["EU AI Act Art. 5", "EU AI Act Art. 9"]
            )
        
        # High Risk AI Systems (Annex III)
        if input_data.used_in_critical_infra or \
           input_data.affects_access_to_services or \
           "law enforcement" in input_data.deployment_context.lower() or \
           "education" in input_data.deployment_context.lower():
            domain = "Annex III: Critical Infrastructure / Essential Services"
            return RiskTierResult(
                tier=RiskTier.HIGH,
                blocking=False,
                annex_iii_domain=domain,
                explanation=f"The system is classified as HIGH risk under {domain} per EU AI Act Annex III.",
                regulatory_basis=["EU AI Act Art. 9", "EU AI Act Annex III"]
            )
            
        # Limited Risk (Art. 52)
        if "chatbot" in input_data.use_case.lower() or "emotion recognition" in input_data.use_case.lower():
            return RiskTierResult(
                tier=RiskTier.LIMITED,
                blocking=False,
                explanation="The system is classified as LIMITED risk (e.g., chatbot, emotion recognition) requiring transparency disclosures per EU AI Act Art. 52.",
                regulatory_basis=["EU AI Act Art. 9", "EU AI Act Art. 52"]
            )
            
        # Minimal Risk
        return RiskTierResult(
            tier=RiskTier.MINIMAL,
            blocking=False,
            explanation="The system is classified as MINIMAL risk (e.g., spam filters, video games) with no additional regulatory obligations under the EU AI Act.",
            regulatory_basis=["EU AI Act Art. 9"]
        )
