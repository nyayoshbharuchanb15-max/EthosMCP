from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class MitigationMeasure(BaseModel):
    measure: str
    article: str
    description: str


class DPIAResult(BaseModel):
    dpia_required: bool
    risk_level: str
    jurisdictional_conflicts: list[dict[str, str]] = Field(default_factory=list)
    mitigation_measures: list[MitigationMeasure] = Field(default_factory=list)
    articles_triggered: list[str] = Field(default_factory=list)


SPECIAL_CATEGORY_DATA_TYPES: list[str] = [
    "racial_or_ethnic_origin",
    "political_opinions",
    "religious_or_philosophical_beliefs",
    "trade_union_membership",
    "genetic_data",
    "biometric_data",
    "health_data",
    "sex_life_or_sexual_orientation",
    "criminal_convictions",
]

HIGH_RISK_PROCESSING_INDICATORS: list[str] = [
    "systematic_evaluation_of_individuals",
    "large_scale_processing_of_special_categories",
    "systematic_monitoring_of_publicly_accessible_areas",
    "automated_profiling_with_significant_effects",
    "processing_of_vulnerable_persons_data",
    "use_of_new_technologies",
    "data_matching_or_combining_datasets",
    "denial_of_service_or_exclusion",
]


class DPIAAssessmentEngine:
    def assess(self, processing_activity: dict[str, Any]) -> DPIAResult:
        data_types = self._get_list(processing_activity, "data_types")
        _purposes = self._get_list(processing_activity, "purposes")
        scope = processing_activity.get("scope", {})
        if not isinstance(scope, dict):
            scope = {}
        data_volume = scope.get("data_volume", 0)
        data_subject_count = scope.get("data_subject_count", 0)
        is_cross_border = bool(processing_activity.get("cross_border_transfer", False))
        jurisdictions_covered = self._get_list(processing_activity, "jurisdictions_covered")
        children_data = bool(processing_activity.get("children_data", False))
        _vulnerable_data = bool(processing_activity.get("vulnerable_data", False))
        systematic_monitoring = bool(
            processing_activity.get("systematic_monitoring", False)
        )
        automated_profiling = bool(processing_activity.get("automated_profiling", False))
        new_technologies = bool(processing_activity.get("new_technologies", False))

        has_special_category = any(
            dt in SPECIAL_CATEGORY_DATA_TYPES for dt in data_types
        )

        large_scale = (
            data_volume > 100000
            or data_subject_count > 100000
            or (
                has_special_category
                and data_subject_count > 10000
            )
        )

        dpia_required = False
        triggered_articles: list[str] = []
        risk_factors: list[str] = []
        mitigation: list[MitigationMeasure] = []

        if has_special_category:
            dpia_required = True
            triggered_articles.append("Art 35(3)(a)")
            risk_factors.append("special_category_data")
            mitigation.append(
                MitigationMeasure(
                    measure="Special category data handling",
                    article="Art 9",
                    description="Implement enhanced safeguards for special category data: explicit consent, "
                    "employment law necessity, or substantial public interest basis.",
                )
            )

        if large_scale:
            dpia_required = True
            triggered_articles.append("Art 35(3)(b)")
            risk_factors.append("large_scale_processing")
            mitigation.append(
                MitigationMeasure(
                    measure="Large-scale processing safeguards",
                    article="Art 35(3)(b)",
                    description="Implement data minimisation, pseudonymisation, and dedicated DPO oversight.",
                )
            )

        if systematic_monitoring:
            dpia_required = True
            triggered_articles.append("Art 35(3)(c)")
            risk_factors.append("systematic_monitoring")
            mitigation.append(
                MitigationMeasure(
                    measure="Systematic monitoring controls",
                    article="Art 35(3)(c)",
                    description="Deploy transparency notices, access controls, and purpose limitation for monitoring activities.",
                )
            )

        if children_data:
            dpia_required = True
            triggered_articles.append("Art 8")
            risk_factors.append("children_data")
            mitigation.append(
                MitigationMeasure(
                    measure="Children's data protection",
                    article="Art 8",
                    description="Implement age verification and parental consent mechanisms. "
                    "Ensure processing is in the best interest of the child.",
                )
            )

        if automated_profiling:
            dpia_required = True
            triggered_articles.append("Art 22")
            risk_factors.append("automated_profiling")
            mitigation.append(
                MitigationMeasure(
                    measure="Automated decision-making safeguards",
                    article="Art 22",
                    description="Provide right to human intervention, express views, and contest decisions. "
                    "Ensure meaningful information about logic involved.",
                )
            )

        if is_cross_border:
            triggered_articles.append("Art 44-49")
            risk_factors.append("cross_border_transfer")
            mitigation.append(
                MitigationMeasure(
                    measure="Cross-border transfer safeguards",
                    article="Art 44-49",
                    description="Ensure adequate level of protection via adequacy decision, SCCs, BCRs, "
                    "or derogations per Art 49. Document transfer impact assessment.",
                )
            )

        if new_technologies:
            triggered_articles.append("Art 35(1)")
            risk_factors.append("new_technologies")
            mitigation.append(
                MitigationMeasure(
                    measure="New technology risk assessment",
                    article="Art 35(1)",
                    description="Account for novel technological risks in DPIA. Engage DPO and consult "
                    "supervisory authority where residual risk is high.",
                )
            )

        jurisdictional_conflicts = self._assess_jurisdictional_conflicts(
            jurisdictions_covered, is_cross_border
        )

        if len(risk_factors) >= 3:
            risk_level = "HIGH"
        elif len(risk_factors) >= 1:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        return DPIAResult(
            dpia_required=dpia_required,
            risk_level=risk_level,
            jurisdictional_conflicts=jurisdictional_conflicts,
            mitigation_measures=mitigation,
            articles_triggered=sorted(set(triggered_articles)),
        )

    def _get_list(self, d: dict[str, Any], key: str) -> list[str]:
        val = d.get(key, [])
        if not isinstance(val, list):
            return [str(val)] if val else []
        return [str(v) for v in val]

    def _assess_jurisdictional_conflicts(
        self, jurisdictions: list[str], cross_border: bool
    ) -> list[dict[str, str]]:
        conflicts: list[dict[str, str]] = []
        if not cross_border and len(jurisdictions) <= 1:
            return conflicts
        gdpr_equivalent = [j for j in jurisdictions if j.lower() in ("eu", "eea", "united kingdom", "uk", "switzerland", "brazil", "south africa")]
        other = [j for j in jurisdictions if j not in gdpr_equivalent]
        for j in other:
            conflicts.append(
                {
                    "jurisdiction": j,
                    "conflict": f"Potential conflict between GDPR requirements and {j} data protection law",
                    "recommendation": f"Assess adequacy decision or appropriate safeguards under Art 45-46 for data flows involving {j}.",
                }
            )
        if len(gdpr_equivalent) > 1:
            conflicts.append(
                {
                    "jurisdiction": "GDPR jurisdictions",
                    "conflict": "Multiple GDPR-equivalent jurisdictions — ensure one-stop-shop mechanism per Art 56",
                    "recommendation": "Identify lead supervisory authority based on main establishment per Art 56(1).",
                }
            )
        return conflicts
