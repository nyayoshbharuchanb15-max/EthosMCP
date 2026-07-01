from __future__ import annotations


import numpy as np
from pydantic import BaseModel, Field
from scipy import stats as scipy_stats


class DriftFinding(BaseModel):
    metric: str
    drift_score: float
    threshold: float
    drift_detected: bool
    detail: str
    severity: str


class DriftResult(BaseModel):
    data_drift: list[DriftFinding] = Field(default_factory=list)
    concept_drift: list[DriftFinding] = Field(default_factory=list)
    overall_drift_detected: bool = False
    overall_drift_score: float = 0.0


DEFAULT_DRIFT_THRESHOLDS: dict[str, float] = {
    "population_stability_index": 0.25,
    "ks_statistic": 0.05,
    "accuracy_degradation": 0.10,
    "feature_drift": 0.15,
}


class DriftDetector:
    def __init__(self, thresholds: dict[str, float] | None = None) -> None:
        self.thresholds = {**DEFAULT_DRIFT_THRESHOLDS, **(thresholds or {})}

    def check_drift(
        self,
        production_data: np.ndarray | list[list[float]],
        baseline_data: np.ndarray | list[list[float]],
        thresholds: dict[str, float] | None = None,
    ) -> DriftResult:
        prod = np.asarray(production_data, dtype=np.float64)
        base = np.asarray(baseline_data, dtype=np.float64)

        if prod.ndim == 1:
            prod = prod.reshape(-1, 1)
        if base.ndim == 1:
            base = base.reshape(-1, 1)

        if prod.shape[1] != base.shape[1]:
            raise ValueError(
                f"Dimensionality mismatch: production {prod.shape[1]} vs baseline {base.shape[1]}"
            )

        merged_thresholds = {**self.thresholds, **(thresholds or {})}

        data_drift = self._compute_data_drift(prod, base, merged_thresholds)

        concept_drift = self._compute_concept_drift(prod, base, merged_thresholds)

        all_findings = data_drift + concept_drift
        drift_detected = any(f.drift_detected for f in all_findings)

        if all_findings:
            overall_score = float(np.mean([f.drift_score for f in all_findings]))
        else:
            overall_score = 0.0

        return DriftResult(
            data_drift=data_drift,
            concept_drift=concept_drift,
            overall_drift_detected=drift_detected,
            overall_drift_score=round(overall_score, 4),
        )

    def _compute_data_drift(
        self,
        prod: np.ndarray,
        base: np.ndarray,
        thresholds: dict[str, float],
    ) -> list[DriftFinding]:
        findings: list[DriftFinding] = []

        for col_idx in range(prod.shape[1]):
            prod_col = prod[:, col_idx]
            base_col = base[:, col_idx]

            psi = self._compute_psi(base_col, prod_col)
            psi_threshold = thresholds.get("population_stability_index", 0.25)
            findings.append(
                DriftFinding(
                    metric=f"psi_feature_{col_idx}",
                    drift_score=round(psi, 4),
                    threshold=psi_threshold,
                    drift_detected=psi > psi_threshold,
                    detail=f"Population Stability Index for feature {col_idx}: {psi:.4f} "
                    f"(threshold: {psi_threshold})",
                    severity="WARNING" if psi > psi_threshold else "INFO",
                )
            )

            ks_stat, ks_pvalue = scipy_stats.ks_2samp(base_col, prod_col)
            ks_threshold = thresholds.get("ks_statistic", 0.05)
            ks_drift = ks_pvalue < ks_threshold
            findings.append(
                DriftFinding(
                    metric=f"ks_feature_{col_idx}",
                    drift_score=round(ks_stat, 4),
                    threshold=ks_threshold,
                    drift_detected=ks_drift,
                    detail=f"KS test for feature {col_idx}: statistic={ks_stat:.4f}, "
                    f"p-value={ks_pvalue:.6f} (threshold: {ks_threshold})",
                    severity="WARNING" if ks_drift else "INFO",
                )
            )

        overall_psi = float(np.mean([f.drift_score for f in findings if "psi" in f.metric]))
        overall_psi_threshold = thresholds.get("population_stability_index", 0.25)

        if prod.shape[1] > 1:
            findings.append(
                DriftFinding(
                    metric="overall_feature_drift",
                    drift_score=round(overall_psi, 4),
                    threshold=overall_psi_threshold,
                    drift_detected=overall_psi > overall_psi_threshold,
                    detail=f"Overall feature drift (mean PSI): {overall_psi:.4f} "
                    f"(threshold: {overall_psi_threshold})",
                    severity="WARNING" if overall_psi > overall_psi_threshold else "INFO",
                )
            )

        return findings

    def _compute_concept_drift(
        self,
        prod: np.ndarray,
        base: np.ndarray,
        thresholds: dict[str, float],
    ) -> list[DriftFinding]:
        findings: list[DriftFinding] = []

        if prod.shape[0] < 2 or base.shape[0] < 2:
            return findings

        prod_mean = float(np.mean(prod))
        base_mean = float(np.mean(base))
        mean_shift = abs(prod_mean - base_mean) / (abs(base_mean) + 1e-10)

        acc_threshold = thresholds.get("accuracy_degradation", 0.10)
        findings.append(
            DriftFinding(
                metric="concept_drift_mean_shift",
                drift_score=round(mean_shift, 4),
                threshold=acc_threshold,
                drift_detected=mean_shift > acc_threshold,
                detail=f"Concept drift (mean shift): {mean_shift:.4f} "
                f"(baseline mean: {base_mean:.4f}, production mean: {prod_mean:.4f})",
                severity="WARNING" if mean_shift > acc_threshold else "INFO",
            )
        )

        prod_std = float(np.std(prod))
        base_std = float(np.std(base))
        std_ratio = min(prod_std, base_std) / (max(prod_std, base_std) + 1e-10)

        findings.append(
            DriftFinding(
                metric="concept_drift_variance_shift",
                drift_score=round(1.0 - std_ratio, 4),
                threshold=acc_threshold,
                drift_detected=(1.0 - std_ratio) > acc_threshold,
                detail=f"Concept drift (variance shift): ratio={std_ratio:.4f} "
                f"(baseline std: {base_std:.4f}, production std: {prod_std:.4f})",
                severity="WARNING" if (1.0 - std_ratio) > acc_threshold else "INFO",
            )
        )

        t_stat, t_pvalue = scipy_stats.ttest_ind(base.flatten(), prod.flatten())
        findings.append(
            DriftFinding(
                metric="concept_drift_ttest",
                drift_score=round(abs(t_stat), 4),
                threshold=acc_threshold,
                drift_detected=t_pvalue < 0.05,
                detail=f"Concept drift (t-test): statistic={t_stat:.4f}, "
                f"p-value={t_pvalue:.6f}",
                severity="WARNING" if t_pvalue < 0.05 else "INFO",
            )
        )

        return findings

    def _compute_psi(self, expected: np.ndarray, actual: np.ndarray, bins: int = 10) -> float:
        combined = np.concatenate([expected, actual])
        if np.std(combined) < 1e-10:
            return 0.0

        hist_expected, edges = np.histogram(expected, bins=bins)
        hist_actual, _ = np.histogram(actual, bins=edges)

        pct_expected = hist_expected / len(expected)
        pct_actual = hist_actual / len(actual)

        psi = 0.0
        for e, a in zip(pct_expected, pct_actual):
            e = max(e, 1e-10)
            a = max(a, 1e-10)
            psi += (a - e) * np.log(a / e)

        return float(psi)
