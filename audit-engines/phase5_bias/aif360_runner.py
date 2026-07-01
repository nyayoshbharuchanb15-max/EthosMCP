from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AIF360AuditResult(BaseModel):
    disparate_impact: float | None = None
    statistical_parity_difference: float | None = None
    equal_opportunity_difference: float | None = None
    average_odds_difference: float | None = None
    theil_index: float | None = None
    metrics: dict[str, float] = Field(default_factory=dict)


class AIF360BiasAuditor:
    def run_audit(
        self,
        dataset: Any,
        privileged_groups: list[dict[str, Any]] | None = None,
        unprivileged_groups: list[dict[str, Any]] | None = None,
    ) -> AIF360AuditResult:
        if privileged_groups is None:
            privileged_groups = []
        if unprivileged_groups is None:
            unprivileged_groups = []

        metrics: dict[str, float] = {}

        try:
            from aif360.metrics import BinaryLabelDatasetMetric, ClassificationMetric
            from aif360.datasets import BinaryLabelDataset

            if isinstance(dataset, BinaryLabelDataset):
                bld_metric = BinaryLabelDatasetMetric(
                    dataset,
                    privileged_groups=privileged_groups,
                    unprivileged_groups=unprivileged_groups,
                )
                di = float(bld_metric.disparate_impact())
                spd = float(bld_metric.statistical_parity_difference())
                metrics["disparate_impact"] = di
                metrics["statistical_parity_difference"] = spd

                if hasattr(dataset, "labels") and dataset.labels is not None:
                    cm = ClassificationMetric(
                        dataset,
                        dataset,
                        privileged_groups=privileged_groups,
                        unprivileged_groups=unprivileged_groups,
                    )
                    metrics["equal_opportunity_difference"] = float(
                        cm.equal_opportunity_difference()
                    )
                    metrics["average_odds_difference"] = float(
                        cm.average_odds_difference()
                    )
                    metrics["theil_index"] = float(cm.theil_index())

        except ImportError:
            pass

        return AIF360AuditResult(
            disparate_impact=metrics.get("disparate_impact"),
            statistical_parity_difference=metrics.get("statistical_parity_difference"),
            equal_opportunity_difference=metrics.get("equal_opportunity_difference"),
            average_odds_difference=metrics.get("average_odds_difference"),
            theil_index=metrics.get("theil_index"),
            metrics=metrics,
        )
