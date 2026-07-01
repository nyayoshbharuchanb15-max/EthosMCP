import pytest


class TestEUAIActRiskClassifier:

    UNACCEPTABLE_USE_CASES = [
        "real-time remote biometric identification in publicly accessible spaces for law enforcement",
        "social scoring by public authorities",
        "exploitation of vulnerabilities of persons",
    ]

    ANNEX3_BIOMETRICS = {
        "use_case": "remote_biometric_identification",
        "deployment_context": "public_sector",
        "processes_biometric_data": True,
        "used_in_critical_infra": False,
        "affects_access_to_services": False,
        "autonomous_decision": True,
    }

    CHATBOT = {
        "use_case": "chatbot",
        "deployment_context": "B2C",
        "processes_biometric_data": False,
        "used_in_critical_infra": False,
        "affects_access_to_services": False,
        "autonomous_decision": False,
    }

    SPAM_FILTER = {
        "use_case": "spam_filter",
        "deployment_context": "B2B",
        "processes_biometric_data": False,
        "used_in_critical_infra": False,
        "affects_access_to_services": False,
        "autonomous_decision": False,
    }

    @staticmethod
    def classify_risk(use_case: str, deployment_context: str,
                      processes_biometric: bool, critical_infra: bool,
                      affects_access: bool, autonomous: bool) -> tuple[str, str]:
        prohibited = [
            "real-time remote biometric identification in publicly accessible spaces for law enforcement",
            "social scoring by public authorities",
            "exploitation of vulnerabilities of persons",
        ]
        if use_case in prohibited:
            return "UNACCEPTABLE", "Art. 5"

        if use_case in ("remote_biometric_identification", "biometric_categorisation",
                        "biometric_emotion_recognition"):
            if processes_biometric:
                return "HIGH", "Art. 6(2) – Annex III(1) — Notified Body required"

        high_risk_use_cases = (
            "creditworthiness_assessment", "insurance_risk_assessment",
            "recruitment_screening", "employee_performance_evaluation",
            "educational_access", "law_enforcement_risk_assessment",
            "migration_asylum_processing", "critical_infrastructure_operation",
        )
        if use_case in high_risk_use_cases:
            return "HIGH", "Art. 6(2) – Annex III"

        if use_case in ("chatbot", "content_moderation", "recommendation"):
            return "LIMITED", "Art. 50 — Transparency obligations"

        return "MINIMAL", "No specific obligations beyond existing law"

    @staticmethod
    def get_conformity_path(use_case: str, processes_biometric: bool) -> str:
        if use_case in ("remote_biometric_identification",) and processes_biometric:
            return "notified_body"
        if use_case in ("creditworthiness_assessment", "insurance_risk_assessment"):
            return "self_assessment"
        if use_case in ("recruitment_screening", "educational_access"):
            return "self_assessment"
        return "self_assessment"

    def test_prohibited_system_returns_unacceptable(self):
        risk_tier, article = self.classify_risk(
            use_case=self.UNACCEPTABLE_USE_CASES[0],
            deployment_context="public_sector",
            processes_biometric=True,
            critical_infra=False,
            affects_access=False,
            autonomous=True,
        )
        assert risk_tier == "UNACCEPTABLE"
        assert "Art. 5" in article

    def test_annex3_biometrics_returns_high_risk_notified_body(self):
        risk_tier, article = self.classify_risk(
            use_case=self.ANNEX3_BIOMETRICS["use_case"],
            deployment_context=self.ANNEX3_BIOMETRICS["deployment_context"],
            processes_biometric=self.ANNEX3_BIOMETRICS["processes_biometric_data"],
            critical_infra=self.ANNEX3_BIOMETRICS["used_in_critical_infra"],
            affects_access=self.ANNEX3_BIOMETRICS["affects_access_to_services"],
            autonomous=self.ANNEX3_BIOMETRICS["autonomous_decision"],
        )
        assert risk_tier == "HIGH"
        assert "Notified Body" in article

    def test_chatbot_returns_limited_risk(self):
        risk_tier, article = self.classify_risk(
            use_case=self.CHATBOT["use_case"],
            deployment_context=self.CHATBOT["deployment_context"],
            processes_biometric=self.CHATBOT["processes_biometric_data"],
            critical_infra=self.CHATBOT["used_in_critical_infra"],
            affects_access=self.CHATBOT["affects_access_to_services"],
            autonomous=self.CHATBOT["autonomous_decision"],
        )
        assert risk_tier == "LIMITED"
        assert "Transparency" in article

    def test_spam_filter_returns_minimal_risk(self):
        risk_tier, article = self.classify_risk(
            use_case=self.SPAM_FILTER["use_case"],
            deployment_context=self.SPAM_FILTER["deployment_context"],
            processes_biometric=self.SPAM_FILTER["processes_biometric_data"],
            critical_infra=self.SPAM_FILTER["used_in_critical_infra"],
            affects_access=self.SPAM_FILTER["affects_access_to_services"],
            autonomous=self.SPAM_FILTER["autonomous_decision"],
        )
        assert risk_tier == "MINIMAL"

    def test_conformity_path_biometrics_requires_notified_body(self):
        path = self.get_conformity_path("remote_biometric_identification", True)
        assert path == "notified_body"

    def test_conformity_path_hrm_tool_allows_self_assessment(self):
        path = self.get_conformity_path("recruitment_screening", True)
        assert path == "self_assessment"
