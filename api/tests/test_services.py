from services.risk_classifier import RiskClassifierService
from models.audit_models import RiskClassificationInput, RiskTier

def test_risk_classifier_prohibited():
    service = RiskClassifierService()
    input_data = RiskClassificationInput(
        system_name="Surveillance Bot",
        use_case="biometric mass surveillance",
        deployment_context="Public space",
        processes_biometric_data=True,
        used_in_critical_infra=False,
        affects_access_to_services=False,
        autonomous_decision=True
    )
    result = service.classify(input_data)
    assert result.tier == RiskTier.PROHIBITED
    assert result.blocking is True

def test_risk_classifier_high_risk():
    service = RiskClassifierService()
    input_data = RiskClassificationInput(
        system_name="Credit Scorer",
        use_case="Loan approval",
        deployment_context="Banking",
        processes_biometric_data=False,
        used_in_critical_infra=False,
        affects_access_to_services=True,
        autonomous_decision=True
    )
    result = service.classify(input_data)
    assert result.tier == RiskTier.HIGH
    assert result.blocking is False
