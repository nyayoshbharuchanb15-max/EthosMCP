from __future__ import annotations

import os

from pydantic import BaseModel, Field


class ThresholdFinding(BaseModel):
    metric: str
    value: float
    threshold: float
    passed: bool
    protected_class: str | None = None
    severity: str
    regulation: str
    article: str
    description: str


class ThresholdPolicyResult(BaseModel):
    findings: list[ThresholdFinding] = Field(default_factory=list)
    overall_pass: bool = False


DEFAULT_THRESHOLDS: dict[str, float] = {
    "demographic_parity_difference": 0.10,
    "equalized_odds_difference": 0.10,
    "equal_opportunity_difference": 0.10,
    "disparate_impact_ratio": 0.80,
    "average_odds_difference": 0.10,
    "statistical_parity_difference": 0.10,
    "theil_index": 0.20,
}

PROTECTED_CLASS_THRESHOLD_OVERRIDES_KEY = "BIAS_THRESHOLD_OVERRIDES"


class BiasThresholdPolicy:
    def __init__(self) -> None:
        self._defaults = dict(DEFAULT_THRESHOLDS)
        self._protected_class_overrides: dict[str, dict[str, float]] = {}
        self._load_env_overrides()

    def _load_env_overrides(self) -> None:
        raw = os.environ.get(PROTECTED_CLASS_THRESHOLD_OVERRIDES_KEY, "")
        if not raw:
            return
        try:
            import json
            overrides = json.loads(raw)
            if isinstance(overrides, dict):
                for protected_class, thresholds in overrides.items():
                    if isinstance(thresholds, dict):
                        self._protected_class_overrides[protected_class] = {
                            k: float(v) for k, v in thresholds.items()
                        }
        except (json.JSONDecodeError, TypeError, ValueError):
            pass

    def evaluate(
        self,
        metrics: dict[str, float],
        protected_class: str | None = None,
    ) -> ThresholdPolicyResult:
        findings: list[ThresholdFinding] = []
        applicable_thresholds = dict(self._defaults)

        if protected_class and protected_class in self._protected_class_overrides:
            applicable_thresholds.update(
                self._protected_class_overrides[protected_class]
            )

        for metric_name, value in metrics.items():
            threshold = applicable_thresholds.get(metric_name)
            if threshold is None:
                continue
            if metric_name == "disparate_impact_ratio":
                passed = value >= threshold
            else:
                passed = value <= threshold
            severity = "WARNING" if not passed else "INFO"
            findings.append(
                ThresholdFinding(
                    metric=metric_name,
                    value=value,
                    threshold=threshold,
                    passed=passed,
                    protected_class=protected_class,
                    severity=severity,
                    regulation="EU AI Act",
                    article="Art 10(2)(f)",
                    description=(
                        f"{'Passed' if passed else 'Failed'} — {metric_name}={value:.4f} "
                        f"(threshold: {threshold})"
                        + (f" for protected class '{protected_class}'" if protected_class else "")
                    ),
                )
            )

        overall_pass = all(f.passed for f in findings)
        return ThresholdPolicyResult(
            findings=findings,
            overall_pass=overall_pass,
        )

    def get_applicable_threshold(
        self, metric_name: str, protected_class: str | None = None
    ) -> float | None:
        if protected_class and protected_class in self._protected_class_overrides:
            override = self._protected_class_overrides[protected_class].get(metric_name)
            if override is not None:
                return override
        return self._defaults.get(metric_name)
