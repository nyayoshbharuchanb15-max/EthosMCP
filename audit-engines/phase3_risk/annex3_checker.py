from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AnnexIIICheckResult(BaseModel):
    applicable_categories: list[dict[str, Any]] = Field(default_factory=list)
    references: list[str] = Field(default_factory=list)


ANNEX_III_CATEGORIES: dict[str, dict[str, Any]] = {
    "biometric": {
        "id": "annex3_1",
        "title": "Biometric categorisation and identification systems",
        "article": "Annex III §1",
        "description": "AI systems intended to be used for biometric categorisation of natural persons or for real-time remote biometric identification.",
        "prohibited_subset": [
            "real_time_remote_biometric_id_public_space_law_enforcement",
            "biometric_categorisation_sensitive_attributes_inference",
            "untargeted_scraping_of_facial_images",
        ],
    },
    "critical_infrastructure": {
        "id": "annex3_2",
        "title": "Critical infrastructure safety components",
        "article": "Annex III §2",
        "description": "AI systems intended to be used as safety components in the management and operation of critical digital infrastructure, road traffic, or water, gas, electricity supply.",
        "prohibited_subset": [],
    },
    "education": {
        "id": "annex3_3",
        "title": "Educational and vocational access",
        "article": "Annex III §3",
        "description": "AI systems used to determine access or admission to educational and vocational training institutions, or to evaluate learning outcomes.",
        "prohibited_subset": [],
    },
    "employment": {
        "id": "annex3_4",
        "title": "Employment and worker management",
        "article": "Annex III §4",
        "description": "AI systems used for recruitment, hiring, promotion, performance evaluation, or termination of employment relationships.",
        "prohibited_subset": [],
    },
    "essential_services": {
        "id": "annex3_5",
        "title": "Access to essential services (credit, insurance, benefits)",
        "article": "Annex III §5",
        "description": "AI systems used to evaluate creditworthiness or establish credit scores, or to make decisions about access to essential services and benefits.",
        "prohibited_subset": [],
    },
    "law_enforcement": {
        "id": "annex3_6",
        "title": "Law enforcement",
        "article": "Annex III §6",
        "description": "AI systems intended to be used by law enforcement authorities for polygraph-based interrogation, crime prediction, or evidence assessment.",
        "prohibited_subset": [
            "predictive_policing_individual_profiling",
            "polygraph_emotional_state_detection",
        ],
    },
    "migration": {
        "id": "annex3_7",
        "title": "Migration, asylum, border control",
        "article": "Annex III §7",
        "description": "AI systems used for migration, asylum, and border control management, including visa application processing and authenticity verification.",
        "prohibited_subset": [],
    },
    "justice": {
        "id": "annex3_8",
        "title": "Administration of justice and democratic processes",
        "article": "Annex III §8",
        "description": "AI systems intended to assist judicial authorities in researching and interpreting facts and law, or to influence democratic processes.",
        "prohibited_subset": [],
    },
}


class AnnexIIIChecker:
    def check(self, system_descriptor: dict[str, Any]) -> AnnexIIICheckResult:
        applicable: list[dict[str, Any]] = []
        references: list[str] = []

        use_case = str(system_descriptor.get("use_case", "")).lower()
        intended_purpose = str(system_descriptor.get("intended_purpose", "")).lower()
        domain = str(system_descriptor.get("domain", "")).lower()
        combined = f"{use_case} {intended_purpose} {domain}"

        keyword_map: dict[str, list[str]] = {
            "biometric": [
                "biometric", "facial recognition", "face recognition", "fingerprint",
                "iris scan", "gait analysis", "voiceprint", "emotion recognition",
            ],
            "critical_infrastructure": [
                "critical infrastructure", "power grid", "water supply", "gas supply",
                "road traffic", "nuclear", "transport safety", "traffic management",
            ],
            "education": [
                "education", "admission", "exam", "grading", "assessment", "vocational",
                "learning", "student", "school", "university", "training",
            ],
            "employment": [
                "employment", "recruitment", "hiring", "promotion", "performance review",
                "worker", "staff", "hr", "human resources", "termination", "cv screening",
            ],
            "essential_services": [
                "credit", "credit score", "creditworthiness", "insurance", "underwriting",
                "benefits", "social security", "lending", "loan", "mortgage",
            ],
            "law_enforcement": [
                "law enforcement", "police", "crime", "forensic", "polygraph",
                "evidence", "investigation", "surveillance", "criminal",
            ],
            "migration": [
                "migration", "asylum", "border control", "visa", "refugee",
                "immigration", "travel document", "passport verification",
            ],
            "justice": [
                "justice", "court", "judicial", "legal", "tribunal", "dispute resolution",
                "mediation", "democratic process", "election",
            ],
        }

        explicit_categories = system_descriptor.get("annex_iii_categories", [])
        if isinstance(explicit_categories, list):
            for cat_ref in explicit_categories:
                if isinstance(cat_ref, str):
                    for cat_id, cat_info in ANNEX_III_CATEGORIES.items():
                        if cat_ref == cat_id or cat_ref == cat_info["id"]:
                            if cat_info not in applicable:
                                applicable.append(cat_info)
                                references.append(cat_info["article"])
                elif isinstance(cat_ref, dict):
                    cat_id = str(cat_ref.get("id", ""))
                    for cat_info in ANNEX_III_CATEGORIES.values():
                        if cat_id == cat_info["id"]:
                            if cat_info not in applicable:
                                applicable.append(cat_info)
                                references.append(cat_info["article"])

        for cat_id, cat_info in ANNEX_III_CATEGORIES.items():
            if cat_info in applicable:
                continue
            keywords = keyword_map.get(cat_id, [])
            for kw in keywords:
                if kw in combined:
                    applicable.append(cat_info)
                    references.append(cat_info["article"])
                    break

        return AnnexIIICheckResult(
            applicable_categories=applicable,
            references=references,
        )

    def is_prohibited_subset(self, category: str, use_case: str) -> bool:
        cat_info = ANNEX_III_CATEGORIES.get(category)
        if not cat_info:
            return False
        prohibited = cat_info.get("prohibited_subset", [])
        normalized_case = use_case.replace(" ", "_").lower()
        for item in prohibited:
            if item in normalized_case or normalized_case in item:
                return True
        return False
