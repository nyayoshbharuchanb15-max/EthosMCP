from __future__ import annotations

import logging
from typing import Any

import numpy as np
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class LIMEExplanationResult(BaseModel):
    local_explanation: dict[str, float] = Field(default_factory=dict)
    feature_weights: list[dict[str, Any]] = Field(default_factory=list)
    intercept: float | None = None
    prediction: list[float] | None = None
    mode: str = "tabular"
    error: str | None = None


class LIMEExplainer:
    def __init__(self, mode: str = "tabular") -> None:
        self.mode = mode
        self._lime_available = False
        try:
            import lime  # noqa: F401
            self._lime_available = True
        except ImportError:
            logger.warning("LIME library not available. Install with: pip install lime")

    def explain(
        self,
        model: Any,
        X_sample: np.ndarray,
        feature_names: list[str] | None = None,
        mode: str | None = None,
    ) -> LIMEExplanationResult:
        mode = mode or self.mode
        if feature_names is None:
            feature_names = [f"feature_{i}" for i in range(X_sample.shape[1])]

        if not self._lime_available:
            return self._fallback_explain(model, X_sample, feature_names, mode)

        try:
            if len(X_sample.shape) == 1:
                X_sample = X_sample.reshape(1, -1)

            if mode == "tabular":
                return self._explain_tabular(model, X_sample, feature_names)
            elif mode == "text":
                return self._explain_text(model, X_sample, feature_names)
            else:
                return self._explain_tabular(model, X_sample, feature_names)

        except Exception as e:
            logger.error(f"LIME explanation failed: {e}")
            return self._fallback_explain(model, X_sample, feature_names, mode, error=str(e))

    def _explain_tabular(
        self,
        model: Any,
        X_sample: np.ndarray,
        feature_names: list[str],
    ) -> LIMEExplanationResult:
        import lime.lime_tabular

        instance = X_sample[0] if X_sample.shape[0] > 0 else X_sample

        categorical_features = []
        categorical_names = {}
        for i in range(len(feature_names)):
            unique_vals = np.unique(X_sample[:, i])
            if len(unique_vals) < 10 and unique_vals.dtype.kind in ("i", "u", "b"):
                categorical_features.append(i)
                categorical_names[i] = [str(v) for v in unique_vals]

        explainer = lime.lime_tabular.LimeTabularExplainer(
            X_sample,
            feature_names=feature_names,
            class_names=["prediction"],
            categorical_features=categorical_features,
            categorical_names=categorical_names,
            mode="regression",
        )

        predict_fn = None
        if hasattr(model, "predict_proba"):
            predict_fn = model.predict_proba
        elif hasattr(model, "predict"):
            predict_fn = model.predict

        if predict_fn is None:
            return self._fallback_explain(model, X_sample, feature_names, "tabular")

        exp = explainer.explain_instance(
            instance,
            predict_fn,
            num_features=len(feature_names),
        )

        local_explanation: dict[str, float] = {}
        feature_weights: list[dict[str, Any]] = []
        for feat, weight in exp.as_list():
            local_explanation[feat] = float(weight)
            feature_weights.append({"feature": feat, "weight": float(weight)})

        return LIMEExplanationResult(
            local_explanation=local_explanation,
            feature_weights=feature_weights,
            intercept=float(exp.intercept[0]) if hasattr(exp, "intercept") and exp.intercept is not None else None,
            prediction=exp.predict_proba if hasattr(exp, "predict_proba") else None,
            mode="tabular",
        )

    def _explain_text(
        self,
        model: Any,
        X_sample: np.ndarray,
        feature_names: list[str],
    ) -> LIMEExplanationResult:
        import lime.lime_text

        text_samples = []
        for row in X_sample:
            if isinstance(row, bytes):
                text_samples.append(row.decode("utf-8", errors="replace"))
            else:
                text_samples.append(str(row))

        explainer = lime.lime_text.LimeTextExplainer(class_names=["negative", "positive"])
        predict_fn = None
        if hasattr(model, "predict_proba"):
            predict_fn = model.predict_proba
        elif hasattr(model, "predict"):
            predict_fn = lambda x: model.predict(x)  # noqa: E731

        if predict_fn is None or not text_samples:
            return self._fallback_explain(model, X_sample, feature_names, "text")

        exp = explainer.explain_instance(
            text_samples[0],
            predict_fn,
            num_features=min(10, len(feature_names)),
        )

        local_explanation: dict[str, float] = {}
        feature_weights: list[dict[str, Any]] = []
        for feat, weight in exp.as_list():
            local_explanation[feat] = float(weight)
            feature_weights.append({"feature": feat, "weight": float(weight)})

        return LIMEExplanationResult(
            local_explanation=local_explanation,
            feature_weights=feature_weights,
            mode="text",
        )

    def _fallback_explain(
        self,
        model: Any,
        X_sample: np.ndarray,
        feature_names: list[str],
        mode: str,
        error: str | None = None,
    ) -> LIMEExplanationResult:
        if len(X_sample.shape) == 1:
            X_sample = X_sample.reshape(1, -1)
        instance = X_sample[0] if X_sample.shape[0] > 0 else X_sample
        local_explanation = {feature_names[i]: float(instance[i]) for i in range(min(len(feature_names), len(instance)))}
        return LIMEExplanationResult(
            local_explanation=local_explanation,
            feature_weights=[{"feature": k, "weight": v} for k, v in local_explanation.items()],
            mode=mode,
            error=error,
        )
