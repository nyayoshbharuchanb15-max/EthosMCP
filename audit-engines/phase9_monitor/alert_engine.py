from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ExceededThreshold(BaseModel):
    metric: str
    current_value: float
    threshold: float
    severity: str


class AlertEvaluationResult(BaseModel):
    exceeded_thresholds: list[ExceededThreshold] = Field(default_factory=list)
    reaudit_triggered: bool = False
    alert_severity: str = "INFO"
    reaudit_reason: str | None = None


SEVERITY_ORDER: dict[str, int] = {
    "INFO": 0,
    "WARNING": 1,
    "HIGH": 2,
    "CRITICAL": 3,
    "BLOCKER": 4,
}

REAUDIT_TRIGGER_SEVERITIES: set[str] = {"HIGH", "CRITICAL", "BLOCKER"}
REAUDIT_MIN_EXCEEDED_COUNT: int = 2


class AlertEngine:
    def evaluate_thresholds(
        self,
        metrics: dict[str, float],
        thresholds: dict[str, dict[str, Any]],
    ) -> AlertEvaluationResult:
        exceeded: list[ExceededThreshold] = []

        for metric_name, current_value in metrics.items():
            if metric_name not in thresholds:
                continue
            threshold_config = thresholds[metric_name]
            threshold_value = threshold_config.get("value", float("inf"))
            direction = threshold_config.get("direction", "above")
            severity = threshold_config.get("severity", "WARNING")

            if direction == "above":
                threshold_exceeded = current_value > threshold_value
            elif direction == "below":
                threshold_exceeded = current_value < threshold_value
            elif direction == "outside":
                threshold_exceeded = abs(current_value) > abs(threshold_value)
            else:
                threshold_exceeded = current_value > threshold_value

            if threshold_exceeded:
                exceeded.append(
                    ExceededThreshold(
                        metric=metric_name,
                        current_value=current_value,
                        threshold=threshold_value,
                        severity=severity,
                    )
                )

        max_severity = "INFO"
        for exc in exceeded:
            if SEVERITY_ORDER.get(exc.severity, 0) > SEVERITY_ORDER.get(max_severity, 0):
                max_severity = exc.severity

        reaudit_needed, reason = self.should_trigger_reaudit(exceeded, max_severity)

        return AlertEvaluationResult(
            exceeded_thresholds=exceeded,
            reaudit_triggered=reaudit_needed,
            alert_severity=max_severity,
            reaudit_reason=reason,
        )

    def should_trigger_reaudit(
        self,
        exceeded: list[ExceededThreshold],
        severity: str,
    ) -> tuple[bool, str | None]:
        if not exceeded:
            return False, None

        if severity in REAUDIT_TRIGGER_SEVERITIES and len(exceeded) >= 1:
            reason = (
                f"Re-audit triggered: {len(exceeded)} threshold(s) exceeded "
                f"with severity '{severity}'."
            )
            if len(exceeded) <= 3:
                details = "; ".join(
                    f"{e.metric}={e.current_value:.4f} (threshold: {e.threshold})"
                    for e in exceeded
                )
                reason += f" Details: {details}"
            return True, reason

        if len(exceeded) >= REAUDIT_MIN_EXCEEDED_COUNT:
            reason = (
                f"Re-audit triggered: {len(exceeded)} thresholds exceeded "
                f"(minimum threshold count: {REAUDIT_MIN_EXCEEDED_COUNT})."
            )
            return True, reason

        return False, None
