from __future__ import annotations

import logging
from typing import Any

import numpy as np
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class SHAPExplanationResult(BaseModel):
    global_feature_importance: dict[str, float] = Field(default_factory=dict)
    expected_value: float | None = None
    shap_values: list[list[float]] | None = None
    feature_names: list[str] = Field(default_factory=list)
    explainer_type: str | None = None
    error: str | None = None


class SHAPExplainer:
    def __init__(self, explainer_type: str | None = None) -> None:
        self.explainer_type = explainer_type
        self._shap_available = False
        try:
            import shap  # noqa: F401
            self._shap_available = True
        except ImportError:
            logger.warning("SHAP library not available. Install with: pip install shap")

    def explain(
        self,
        model: Any,
        X_sample: np.ndarray,
        feature_names: list[str] | None = None,
    ) -> SHAPExplanationResult:
        if feature_names is None:
            feature_names = [f"feature_{i}" for i in range(X_sample.shape[1])]

        if not self._shap_available:
            return self._fallback_explain(model, X_sample, feature_names)

        try:
            import shap
            explainer = None
            explainer_type = self.explainer_type

            if explainer_type is None or explainer_type == "tree":
                try:
                    explainer = shap.TreeExplainer(model)
                    explainer_type = "TreeExplainer"
                except Exception:
                    pass

            if explainer is None and (explainer_type is None or explainer_type == "kernel"):
                try:
                    background = X_sample[:100] if len(X_sample) > 100 else X_sample
                    explainer = shap.KernelExplainer(model.predict, background)
                    explainer_type = "KernelExplainer"
                except Exception:
                    pass

            if explainer is None and (explainer_type is None or explainer_type == "deep"):
                try:
                    explainer = shap.DeepExplainer(model, X_sample[:100])
                    explainer_type = "DeepExplainer"
                except Exception:
                    pass

            if explainer is None:
                try:
                    explainer = shap.Explainer(model, X_sample[:100])
                    explainer_type = "Explainer"
                except Exception:
                    pass

            if explainer is None:
                return self._fallback_explain(model, X_sample, feature_names)

            shap_values = explainer(X_sample)

            if hasattr(shap_values, "values"):
                raw_values = shap_values.values
            else:
                raw_values = shap_values

            if hasattr(raw_values, "tolist"):
                raw_values = raw_values.tolist()

            if isinstance(raw_values, list) and len(raw_values) > 0:
                if isinstance(raw_values[0], list):
                    global_importance = {
                        feature_names[i]: float(abs(np.mean([row[i] for row in raw_values])))
                        for i in range(len(feature_names))
                    }
                else:
                    global_importance = {
                        feature_names[i]: float(abs(raw_values[i]))
                        for i in range(len(feature_names))
                    }
            else:
                global_importance = {f: 0.0 for f in feature_names}

            expected_value = None
            if hasattr(shap_values, "base_values"):
                base = shap_values.base_values
                if hasattr(base, "tolist"):
                    base = base.tolist()
                if isinstance(base, list):
                    expected_value = float(base[0]) if base else None
                else:
                    expected_value = float(base) if base is not None else None
            elif hasattr(explainer, "expected_value"):
                ev = explainer.expected_value
                if hasattr(ev, "tolist"):
                    ev = ev.tolist()
                if isinstance(ev, list):
                    expected_value = float(ev[0]) if ev else None
                else:
                    expected_value = float(ev) if ev is not None else None

            return SHAPExplanationResult(
                global_feature_importance=dict(
                    sorted(global_importance.items(), key=lambda x: x[1], reverse=True)
                ),
                expected_value=expected_value,
                shap_values=raw_values if isinstance(raw_values, list) else None,
                feature_names=feature_names,
                explainer_type=explainer_type,
            )

        except Exception as e:
            logger.error(f"SHAP explanation failed: {e}")
            return self._fallback_explain(model, X_sample, feature_names, error=str(e))

    def _fallback_explain(
        self,
        model: Any,
        X_sample: np.ndarray,
        feature_names: list[str],
        error: str | None = None,
    ) -> SHAPExplanationResult:
        try:
            if hasattr(model, "feature_importances_"):
                importance = model.feature_importances_
                if hasattr(importance, "tolist"):
                    importance = importance.tolist()
                global_importance = {
                    feature_names[i]: float(abs(importance[i]))
                    for i in range(min(len(feature_names), len(importance)))
                }
            elif hasattr(model, "coef_"):
                coef = model.coef_
                if hasattr(coef, "tolist"):
                    coef = coef.tolist()
                if isinstance(coef, list) and len(coef) > 0:
                    coef = coef[0]
                global_importance = {
                    feature_names[i]: float(abs(coef[i]))
                    for i in range(min(len(feature_names), len(coef)))
                }
            else:
                global_importance = {f: 0.0 for f in feature_names}

            return SHAPExplanationResult(
                global_feature_importance=dict(
                    sorted(global_importance.items(), key=lambda x: x[1], reverse=True)
                ),
                feature_names=feature_names,
                error=error,
            )
        except Exception:
            return SHAPExplanationResult(
                global_feature_importance={f: 0.0 for f in feature_names},
                feature_names=feature_names,
                error=error or "Could not compute SHAP explanation",
            )
