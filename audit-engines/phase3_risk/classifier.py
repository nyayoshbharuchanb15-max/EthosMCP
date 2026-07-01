from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel


Tier = Literal["UNACCEPTABLE", "HIGH", "LIMITED", "MINIMAL"]


class ClassificationResult(BaseModel):
    tier: Tier
    basis: str
    article: str
    annex_reference: str | None = None
    conformity_path: Literal["NOTIFIED_BODY", "SELF_ASSESSMENT"] = "SELF_ASSESSMENT"


PROHIBITED_ARTICLE_5: dict[str, dict[str, str]] = {
    "subliminal_manipulation": {
        "description": "AI systems deploying subliminal techniques beyond a person's consciousness to materially distort behaviour",
        "article": "Art 5(1)(a)",
    },
    "social_scoring_public_authority": {
        "description": "Social scoring by public authorities for detrimental or unfavourable treatment",
        "article": "Art 5(1)(c)",
    },
    "real_time_remote_biometric_id_public_space": {
        "description": "Real-time remote biometric identification in publicly accessible spaces for law enforcement",
        "article": "Art 5(1)(d)",
    },
    "emotion_recognition_workplace_education": {
        "description": "Emotion recognition systems in workplace and educational institutions",
        "article": "Art 5(1)(f)",
    },
    "biometric_categorisation_sensitive_attributes": {
        "description": "Biometric categorisation systems inferring sensitive attributes (race, religion, sexual orientation)",
        "article": "Art 5(1)(g)",
    },
    "predictive_policing_individual": {
        "description": "Predictive policing based solely on profiling or personality traits of natural persons",
        "article": "Art 5(1)(h)",
    },
}


ANNEX_III_BIOMETRICS = "Annex III §1 — Biometric categorisation and identification systems"
ANNEX_III_CRITICAL_INFRA = "Annex III §2 — Critical infrastructure safety components"
ANNEX_III_EDUCATION = "Annex III §3 — Educational and vocational access"
ANNEX_III_EMPLOYMENT = "Annex III §4 — Employment and worker management"
ANNEX_III_SERVICES = "Annex III §5 — Access to essential services (credit, insurance, benefits)"
ANNEX_III_LAW_ENFORCEMENT = "Annex III §6 — Law enforcement"
ANNEX_III_MIGRATION = "Annex III §7 — Migration, asylum, border control"
ANNEX_III_JUSTICE = "Annex III §8 — Administration of justice and democratic processes"


class EUAIActRiskClassifier:
    def classify(self, system_descriptor: dict[str, Any]) -> ClassificationResult:
        self._validate(system_descriptor)
        prohibited_match = self._check_prohibited(system_descriptor)
        if prohibited_match:
            return ClassificationResult(
                tier="UNACCEPTABLE",
                basis=f"Prohibited AI practice under {prohibited_match['article']}",
                article=prohibited_match["article"],
                annex_reference="Art 5",
                conformity_path="SELF_ASSESSMENT",
            )
        high_risk_match = self._check_high_risk(system_descriptor)
        if high_risk_match:
            return ClassificationResult(
                tier="HIGH",
                basis=f"High-risk AI system under {high_risk_match['article']}",
                article=high_risk_match["article"],
                annex_reference=high_risk_match["annex_reference"],
                conformity_path=high_risk_match["conformity_path"],
            )
        limited_system = system_descriptor.get("limited_risk_system", False)
        if limited_system or system_descriptor.get("intended_use") == "transparency_obligation":
            return ClassificationResult(
                tier="LIMITED",
                basis="Limited risk — transparency obligations under Art 50 apply",
                article="Art 50",
                annex_reference="Title IV",
                conformity_path="SELF_ASSESSMENT",
            )
        return ClassificationResult(
            tier="MINIMAL",
            basis="Minimal risk — no specific regulatory obligations beyond general provisions",
            article="Art 1",
            annex_reference="Title I",
            conformity_path="SELF_ASSESSMENT",
        )

    def _validate(self, system_descriptor: dict[str, Any]) -> None:
        if not isinstance(system_descriptor, dict):
            raise TypeError("system_descriptor must be a dict")

    def _check_prohibited(self, descriptor: dict[str, Any]) -> dict[str, str] | None:
        prohibited_uses = descriptor.get("prohibited_uses", {})
        if not isinstance(prohibited_uses, dict):
            return None
        for key, info in PROHIBITED_ARTICLE_5.items():
            if prohibited_uses.get(key, False):
                return {"article": info["article"], "description": info["description"]}
        use_case = descriptor.get("use_case", "")
        if isinstance(use_case, str):
            for key, info in PROHIBITED_ARTICLE_5.items():
                if key in use_case.replace(" ", "_").lower():
                    return {"article": info["article"], "description": info["description"]}
        return None

    def _check_high_risk(self, descriptor: dict[str, Any]) -> dict[str, str] | None:
        use_case = descriptor.get("use_case", "").lower()
        intended_purpose = descriptor.get("intended_purpose", "").lower()
        combined = f"{use_case} {intended_purpose}"
        annex_categories = descriptor.get("annex_iii_categories", [])
        if not isinstance(annex_categories, list):
            annex_categories = []

        high_risk_map: list[dict[str, Any]] = [
            {
                "keywords": ["biometric", "facial recognition", "fingerprint", "iris", "gait"],
                "article": "Art 6(2) in conjunction with Annex III §1",
                "annex_reference": ANNEX_III_BIOMETRICS,
                "conformity_path": "NOTIFIED_BODY",
            },
            {
                "keywords": ["critical infrastructure", "safety component", "nuclear", "power grid", "water supply", "road traffic"],
                "article": "Art 6(2) in conjunction with Annex III §2",
                "annex_reference": ANNEX_III_CRITICAL_INFRA,
                "conformity_path": "NOTIFIED_BODY",
            },
            {
                "keywords": ["education", "admission", "exam scoring", "learning outcome", "vocational training"],
                "article": "Art 6(2) in conjunction with Annex III §3",
                "annex_reference": ANNEX_III_EDUCATION,
                "conformity_path": "SELF_ASSESSMENT",
            },
            {
                "keywords": ["employment", "hiring", "promotion", "performance evaluation", "worker management"],
                "article": "Art 6(2) in conjunction with Annex III §4",
                "annex_reference": ANNEX_III_EMPLOYMENT,
                "conformity_path": "SELF_ASSESSMENT",
            },
            {
                "keywords": ["credit", "insurance", "benefits", "essential services", "social security"],
                "article": "Art 6(2) in conjunction with Annex III §5",
                "annex_reference": ANNEX_III_SERVICES,
                "conformity_path": "SELF_ASSESSMENT",
            },
            {
                "keywords": ["law enforcement", "polygraph", "lie detection", "crime prediction", "evidence assessment"],
                "article": "Art 6(2) in conjunction with Annex III §6",
                "annex_reference": ANNEX_III_LAW_ENFORCEMENT,
                "conformity_path": "SELF_ASSESSMENT",
            },
            {
                "keywords": ["migration", "asylum", "border control", "visa", "refugee"],
                "article": "Art 6(2) in conjunction with Annex III §7",
                "annex_reference": ANNEX_III_MIGRATION,
                "conformity_path": "SELF_ASSESSMENT",
            },
            {
                "keywords": ["justice", "court", "judicial", "alternative dispute resolution", "legal proceeding"],
                "article": "Art 6(2) in conjunction with Annex III §8",
                "annex_reference": ANNEX_III_JUSTICE,
                "conformity_path": "SELF_ASSESSMENT",
            },
        ]

        for entry in annex_categories:
            if isinstance(entry, dict):
                cat_id = str(entry.get("id", ""))
                if cat_id.startswith("annex3_"):
                    idx = int(cat_id.split("_")[1]) - 1
                    if 0 <= idx < len(high_risk_map):
                        mapping = high_risk_map[idx]
                        return {
                            "article": mapping["article"],
                            "annex_reference": mapping["annex_reference"],
                            "conformity_path": mapping["conformity_path"],
                        }

        for mapping in high_risk_map:
            for kw in mapping["keywords"]:
                if kw in combined:
                    return {
                        "article": mapping["article"],
                        "annex_reference": mapping["annex_reference"],
                        "conformity_path": mapping["conformity_path"],
                    }
        return None
