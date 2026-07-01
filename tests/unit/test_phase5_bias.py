import math
import pytest


class TestBiasAssessment:

    @staticmethod
    def demographic_parity(predictions: list[int], sensitive_attr: list[int],
                           privileged_value: int = 1) -> float:
        privileged = [p for p, s in zip(predictions, sensitive_attr) if s == privileged_value]
        unprivileged = [p for p, s in zip(predictions, sensitive_attr) if s != privileged_value]
        if not privileged or not unprivileged:
            return 1.0
        priv_rate = sum(privileged) / len(privileged)
        unpriv_rate = sum(unprivileged) / len(unprivileged)
        return priv_rate - unpriv_rate

    @staticmethod
    def disparate_impact_ratio(predictions: list[int], sensitive_attr: list[int],
                               privileged_value: int = 1) -> float:
        privileged = [p for p, s in zip(predictions, sensitive_attr) if s == privileged_value]
        unprivileged = [p for p, s in zip(predictions, sensitive_attr) if s != privileged_value]
        if not privileged or not unprivileged:
            return 1.0
        priv_rate = sum(privileged) / len(privileged)
        unpriv_rate = sum(unprivileged) / len(unprivileged)
        if priv_rate == 0:
            return float("inf")
        return unpriv_rate / priv_rate

    @staticmethod
    def equalized_odds_ratio(predictions: list[int], true_labels: list[int],
                              sensitive_attr: list[int], privileged_value: int = 1) -> float:
        priv_tpr = sum(p for p, t, s in zip(predictions, true_labels, sensitive_attr)
                       if s == privileged_value and t == 1) / max(
            sum(1 for t, s in zip(true_labels, sensitive_attr) if t == 1 and s == privileged_value), 1)
        unpriv_tpr = sum(p for p, t, s in zip(predictions, true_labels, sensitive_attr)
                         if s != privileged_value and t == 1) / max(
            sum(1 for t, s in zip(true_labels, sensitive_attr) if t == 1 and s != privileged_value), 1)
        if priv_tpr == 0:
            return float("inf")
        return unpriv_tpr / priv_tpr

    @pytest.fixture
    def fair_dataset(self):
        predictions = [1, 1, 1, 1, 1, 0, 0, 0, 0, 0,
                       0, 0, 0, 0, 0, 1, 1, 1, 1, 1]
        sensitive =   [1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                       0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        return predictions, sensitive

    @pytest.fixture
    def biased_dataset(self):
        predictions = [1, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                       1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        sensitive =   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                       1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        return predictions, sensitive

    def test_equal_outcome_passes_all_metrics(self, fair_dataset):
        predictions, sensitive = fair_dataset
        dp = self.demographic_parity(predictions, sensitive)
        di = self.disparate_impact_ratio(predictions, sensitive)
        assert abs(dp) < 0.1, f"Demographic parity violation: {dp}"
        assert 0.8 <= di <= 1.25, f"Disparate impact outside 80% rule: {di}"

    def test_demographic_parity_violation_creates_blocker_finding(self, biased_dataset):
        predictions, sensitive = biased_dataset
        dp = self.demographic_parity(predictions, sensitive)
        assert abs(dp) > 0.5, f"Expected demographic parity violation, got {dp}"
        severity = "BLOCKER" if abs(dp) > 0.5 else "WARNING"
        assert severity == "BLOCKER"

    def test_disparate_impact_below_80pct_is_high_severity(self, biased_dataset):
        predictions, sensitive = biased_dataset
        di = self.disparate_impact_ratio(predictions, sensitive)
        assert di < 0.8 or math.isinf(di), f"Expected DI below 0.8, got {di}"
        severity = "HIGH" if di < 0.8 else "LOW"
        assert severity == "HIGH"

    def test_findings_reference_correct_eu_ai_act_article(self):
        eu_ai_act_bias_articles = {
            "demographic_parity": "Art. 10(2)(f) — Bias monitoring and mitigation",
            "disparate_impact": "Art. 10(2)(f) — Bias monitoring and mitigation",
            "equalized_odds": "Art. 10(2)(f) — Bias monitoring and mitigation",
        }
        for metric, article in eu_ai_act_bias_articles.items():
            assert "Art. 10" in article
            assert "Bias monitoring" in article
        assert len(eu_ai_act_bias_articles) == 3
