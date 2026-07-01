from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class ExplainabilityReport(BaseModel):
    report_markdown: str
    report_metadata: dict[str, Any] = Field(default_factory=dict)
    regulatory_citations: list[dict[str, str]] = Field(default_factory=list)


REGULATORY_CITATIONS_ART_13: list[dict[str, str]] = [
    {
        "article": "Art 13(1)",
        "description": "High-risk AI systems shall be designed with transparency to enable users to interpret the output",
    },
    {
        "article": "Art 13(2)",
        "description": "Instructions of use shall include the characteristics, capabilities, and limitations of the AI system",
    },
    {
        "article": "Art 13(3)(a)",
        "description": "Information about the identity and contact details of the provider",
    },
    {
        "article": "Art 13(3)(b)",
        "description": "Characteristics, capabilities, and limitations including accuracy, robustness, and explainability metrics",
    },
    {
        "article": "Art 13(3)(d)",
        "description": "Performance metrics including specification of training, validation, and testing datasets",
    },
    {
        "article": "Art 13(3)(e)",
        "description": "Description of the human oversight measures and explainability mechanisms",
    },
    {
        "article": "Art 22 GDPR",
        "description": "Right to meaningful information about the logic involved in automated decision-making",
    },
    {
        "article": "Art 86 GDPR",
        "description": "Right to explanation of decisions made solely on automated processing",
    },
]


class ExplainabilityReportBuilder:
    def build_report(
        self,
        shap_explanation: dict[str, Any] | None = None,
        lime_explanation: dict[str, Any] | None = None,
        input_params: dict[str, Any] | None = None,
    ) -> ExplainabilityReport:
        if shap_explanation is None:
            shap_explanation = {}
        if lime_explanation is None:
            lime_explanation = {}
        if input_params is None:
            input_params = {}

        generated_at = datetime.now(timezone.utc).isoformat()
        sections: list[str] = []

        sections.append("# AI Explainability Report\n")
        sections.append(f"**Generated at:** {generated_at}\n")
        sections.append(f"**System:** {input_params.get('system_name', 'N/A')}\n")
        sections.append(f"**System Version:** {input_params.get('system_version', 'N/A')}\n")
        sections.append(f"**Model:** {input_params.get('model_name', 'N/A')}\n")
        sections.append(f"**Run ID:** {input_params.get('run_id', 'N/A')}\n")
        sections.append("---\n")

        sections.append("## 1. Regulatory Framework\n")
        sections.append(
            "This report addresses the transparency and explainability requirements under:\n"
        )
        for citation in REGULATORY_CITATIONS_ART_13:
            sections.append(f"- **{citation['article']}**: {citation['description']}")
        sections.append("")

        sections.append("## 2. SHAP (SHapley Additive exPlanations) Analysis\n")

        shap_feature_importance = shap_explanation.get("global_feature_importance", {})
        shap_explainer_type = shap_explanation.get("explainer_type", "N/A")
        shap_expected_value = shap_explanation.get("expected_value")

        if shap_feature_importance:
            sections.append(f"**Explainer:** {shap_explainer_type}\n")
            if shap_expected_value is not None:
                sections.append(f"**Baseline (expected) value:** {shap_expected_value:.4f}\n")
            sections.append("\n### Global Feature Importance (SHAP)\n")
            sections.append("| Rank | Feature | Mean |SHAP Value|\n")
            sections.append("|------|---------|-----------------|\n")
            sorted_features = sorted(
                shap_feature_importance.items(), key=lambda x: x[1], reverse=True
            )
            for rank, (feature, importance) in enumerate(sorted_features, 1):
                sections.append(f"| {rank} | {feature} | {importance:.6f} |\n")
            sections.append("")
        else:
            sections.append("*No SHAP explanation data available.*\n")

        sections.append("## 3. LIME (Local Interpretable Model-agnostic Explanations) Analysis\n")

        lime_local = lime_explanation.get("local_explanation", {})
        lime_mode = lime_explanation.get("mode", "N/A")
        lime_intercept = lime_explanation.get("intercept")

        if lime_local:
            sections.append(f"**Explanation mode:** {lime_mode}\n")
            if lime_intercept is not None:
                sections.append(f"**Model intercept:** {lime_intercept:.4f}\n")
            sections.append("\n### Local Feature Contribution (LIME)\n")
            sections.append("| Feature | Weight |\n")
            sections.append("|---------|-------|\n")
            for feature, weight in sorted(
                lime_local.items(), key=lambda x: abs(x[1]), reverse=True
            ):
                sections.append(f"| {feature} | {weight:+.6f} |\n")
            sections.append("")
        else:
            sections.append("*No LIME explanation data available.*\n")

        sections.append("## 4. Explainability Metrics\n")
        sections.append("| Metric | Value |\n")
        sections.append("|--------|-------|\n")

        if shap_feature_importance:
            num_features = len(shap_feature_importance)
            top3_pct = (
                sum(sorted(shap_feature_importance.values(), reverse=True)[:3])
                / sum(shap_feature_importance.values())
                * 100
            )
            sections.append(f"| Number of features explained (SHAP) | {num_features} |\n")
            sections.append(f"| Top-3 feature importance concentration | {top3_pct:.1f}% |\n")

        if lime_local:
            sections.append(f"| Number of local features explained (LIME) | {len(lime_local)} |\n")

        sections.append("")

        sections.append("## 5. Compliance Assessment\n")
        sections.append("| Requirement | Status |\n")
        sections.append("|-------------|--------|\n")

        regulations = input_params.get("regulatory_frameworks", ["EU AI Act", "GDPR"])
        status_map: dict[str, str] = {}

        if shap_feature_importance:
            status_map["Art 13(1) — Transparency (SHAP global explanation)"] = "✅ Compliant"
        else:
            status_map["Art 13(1) — Transparency (SHAP global explanation)"] = "❌ Not Compliant"

        if lime_local:
            status_map["Art 22 GDPR — Logic information (LIME local explanation)"] = "✅ Compliant"
        else:
            status_map["Art 22 GDPR — Logic information (LIME local explanation)"] = "❌ Not Compliant"

        for req, status in status_map.items():
            sections.append(f"| {req} | {status} |\n")
        sections.append("")

        sections.append("## 6. Recommendations\n")
        sections.append(
            "1. **Ensure SHAP analysis is reproducible** — persist background dataset for consistent explanations.\n"
        )
        sections.append(
            "2. **Document feature engineering** — ensure all input features have clear, human-readable names.\n"
        )
        sections.append(
            "3. **Provide user-facing explanation** — translate technical SHAP/LIME values into "
            "natural language explanations for end users per Art 13(3).\n"
        )
        sections.append(
            "4. **Monitor explanation stability** — track feature importance over time to detect concept drift.\n"
        )
        sections.append(
            "5. **Human oversight** — ensure users can override or contest decisions based on explained outputs.\n"
        )
        sections.append("")

        sections.append("---\n")
        sections.append(
            "*This report was automatically generated by the AI Compliance MCP Server explainability pipeline.*\n"
        )

        report_markdown = "".join(sections)

        return ExplainabilityReport(
            report_markdown=report_markdown,
            report_metadata={
                "generated_at": generated_at,
                "system_name": input_params.get("system_name"),
                "model_name": input_params.get("model_name"),
                "shap_available": bool(shap_feature_importance),
                "lime_available": bool(lime_local),
                "regulatory_frameworks": regulations,
            },
            regulatory_citations=list(REGULATORY_CITATIONS_ART_13),
        )
