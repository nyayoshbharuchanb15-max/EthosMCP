from __future__ import annotations

from typing import Any

import numpy as np
from pydantic import BaseModel, Field

from fairlearn.metrics import demographic_parity_difference, equalized_odds_difference


class Finding(BaseModel):
    metric: str
    value: float
    threshold: float
    passed: bool
    severity: str
    regulation: str
    article: str
    description: str


class FairlearnAuditResult(BaseModel):
    disparity_scores: dict[str, float] = Field(default_factory=dict)
    findings: list[Finding] = Field(default_factory=list)
    overall_pass: bool = False


METRIC_THRESHOLDS: dict[str, float] = {
    "demographic_parity_difference": 0.10,
    "equalized_odds_difference": 0.10,
    "equal_opportunity_difference": 0.10,
    "disparate_impact_ratio": 0.80,
}


class FairlearnBiasAuditor:
    def __init__(self, thresholds: dict[str, float] | None = None) -> None:
        self.thresholds = {**METRIC_THRESHOLDS, **(thresholds or {})}

    def run_audit(
        self,
        y_true: list[float] | np.ndarray,
        y_pred: list[float] | np.ndarray,
        sensitive_features: list[Any] | np.ndarray,
    ) -> FairlearnAuditResult:
        y_true_arr = np.asarray(y_true)
        y_pred_arr = np.asarray(y_pred)
        sensitive_arr = np.asarray(sensitive_features)

        findings: list[Finding] = []
        disparity_scores: dict[str, float] = {}

        demo_parity = demographic_parity_difference(
            y_true=y_true_arr,
            y_pred=y_pred_arr,
            sensitive_features=sensitive_arr,
        )
        disparity_scores["demographic_parity_difference"] = float(demo_parity)
        threshold_dp = self.thresholds["demographic_parity_difference"]
        findings.append(
            Finding(
                metric="demographic_parity_difference",
                value=float(demo_parity),
                threshold=threshold_dp,
                passed=float(demo_parity) <= threshold_dp,
                severity="WARNING" if float(demo_parity) > threshold_dp else "INFO",
                regulation="EU AI Act",
                article="Art 10(2)(f)",
                description=f"Demographic parity difference: {demo_parity:.4f} (threshold: {threshold_dp}). "
                f"Measures whether predictions are independent of sensitive attributes.",
            )
        )

        eq_odds = equalized_odds_difference(
            y_true=y_true_arr,
            y_pred=y_pred_arr,
            sensitive_features=sensitive_arr,
        )
        disparity_scores["equalized_odds_difference"] = float(eq_odds)
        threshold_eo = self.thresholds["equalized_odds_difference"]
        findings.append(
            Finding(
                metric="equalized_odds_difference",
                value=float(eq_odds),
                threshold=threshold_eo,
                passed=float(eq_odds) <= threshold_eo,
                severity="WARNING" if float(eq_odds) > threshold_eo else "INFO",
                regulation="EU AI Act",
                article="Art 10(2)(f)",
                description=f"Equalized odds difference: {eq_odds:.4f} (threshold: {threshold_eo}). "
                f"Measures whether TPR and FPR are equal across groups.",
            )
        )

        eq_opp = self._compute_equal_opportunity_difference(
            y_true_arr, y_pred_arr, sensitive_arr
        )
        disparity_scores["equal_opportunity_difference"] = float(eq_opp)
        threshold_eopp = self.thresholds["equal_opportunity_difference"]
        findings.append(
            Finding(
                metric="equal_opportunity_difference",
                value=float(eq_opp),
                threshold=threshold_eopp,
                passed=float(eq_opp) <= threshold_eopp,
                severity="WARNING" if float(eq_opp) > threshold_eopp else "INFO",
                regulation="EU AI Act",
                article="Art 10(2)(f)",
                description=f"Equal opportunity difference: {eq_opp:.4f} (threshold: {threshold_eopp}). "
                f"Measures whether TPR is equal across groups.",
            )
        )

        di_ratio = self._compute_disparate_impact_ratio(
            y_true_arr, y_pred_arr, sensitive_arr
        )
        disparity_scores["disparate_impact_ratio"] = float(di_ratio)
        threshold_di = self.thresholds["disparate_impact_ratio"]
        findings.append(
            Finding(
                metric="disparate_impact_ratio",
                value=float(di_ratio),
                threshold=threshold_di,
                passed=float(di_ratio) >= threshold_di,
                severity="WARNING" if float(di_ratio) < threshold_di else "INFO",
                regulation="EU AI Act",
                article="Art 10(2)(f)",
                description=f"Disparate impact ratio: {di_ratio:.4f} (threshold: {threshold_di}). "
                f"Ratio of favourable outcomes for unprivileged vs privileged groups. "
                f"Values below {threshold_di} indicate adverse impact.",
            )
        )

        overall_pass = all(f.passed for f in findings)

        return FairlearnAuditResult(
            disparity_scores=disparity_scores,
            findings=findings,
            overall_pass=overall_pass,
        )

    def _compute_equal_opportunity_difference(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        sensitive_features: np.ndarray,
    ) -> float:
        groups = np.unique(sensitive_features)
        tprs: list[float] = []
        for group in groups:
            mask = sensitive_features == group
            group_true = y_true[mask]
            group_pred = y_pred[mask]
            tp = np.sum((group_pred == 1) & (group_true == 1))
            fn = np.sum((group_pred == 0) & (group_true == 1))
            tpr = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            tprs.append(tpr)
        return float(np.max(tprs) - np.min(tprs)) if len(tprs) >= 2 else 0.0

    def _compute_disparate_impact_ratio(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        sensitive_features: np.ndarray,
    ) -> float:
        groups = np.unique(sensitive_features)
        if len(groups) < 2:
            return 1.0
        pos_rates: list[float] = []
        for group in groups:
            mask = sensitive_features == group
            group_pred = y_pred[mask]
            rate = float(np.mean(group_pred)) if len(group_pred) > 0 else 0.0
            pos_rates.append(rate)
        min_rate = min(pos_rates)
        max_rate = max(pos_rates)
        if max_rate == 0.0:
            return 1.0
        return min_rate / max_rate
