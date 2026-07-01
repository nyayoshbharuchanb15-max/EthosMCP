from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel


class ConformityPathResult(BaseModel):
    tier: str
    conformity_path: Literal["NOTIFIED_BODY", "SELF_ASSESSMENT"]
    article: str
    article_detail: str
    notified_body_required: bool = False
    technical_documentation_required: bool = True
    eu_declaration_conformity_required: bool = True


NOTIFIED_BODY_REQUIRED_ANNEX_III_SECTIONS: dict[str, dict[str, str]] = {
    "annex3_1": {
        "section": "Annex III §1",
        "title": "Biometric categorisation and identification",
        "article": "Art 43(1)",
    },
    "annex3_2": {
        "section": "Annex III §2",
        "title": "Critical infrastructure safety components",
        "article": "Art 43(1)",
    },
}


class ConformityPathDeterminer:
    def determine(
        self,
        tier: str,
        system_type: str,
        annex_categories: list[dict[str, Any]] | None = None,
    ) -> ConformityPathResult:
        if annex_categories is None:
            annex_categories = []

        upper_tier = tier.upper()

        if upper_tier == "UNACCEPTABLE":
            return ConformityPathResult(
                tier=upper_tier,
                conformity_path="SELF_ASSESSMENT",
                article="Art 5",
                article_detail="Prohibited AI practice — no conformity assessment path. System must not be placed on market.",
                notified_body_required=False,
                technical_documentation_required=False,
                eu_declaration_conformity_required=False,
            )

        category_ids = []
        for cat in annex_categories:
            if isinstance(cat, dict):
                cat_id = cat.get("id", "")
            elif isinstance(cat, str):
                cat_id = cat
            else:
                continue
            category_ids.append(str(cat_id))

        notified_body_required = False
        article_detail = ""
        article = ""

        if upper_tier == "HIGH":
            for cat_id in category_ids:
                if cat_id in NOTIFIED_BODY_REQUIRED_ANNEX_III_SECTIONS:
                    nb_info = NOTIFIED_BODY_REQUIRED_ANNEX_III_SECTIONS[cat_id]
                    notified_body_required = True
                    article = nb_info["article"]
                    article_detail = (
                        f"Notified body required — system falls under {nb_info['section']} "
                        f"({nb_info['title']}). Conformity assessment per Annex VII."
                    )
                    break

            if not notified_body_required:
                article = "Art 43(2)"
                article_detail = (
                    "Self-assessment — system does not fall under notified body requirement. "
                    "Internal control per Annex VI. Technical documentation per Art 11 and Annex IV."
                )

        elif upper_tier == "LIMITED":
            article = "Art 50"
            article_detail = (
                "Limited risk — transparency obligations only. "
                "No conformity assessment required beyond Art 50 disclosure."
            )

        elif upper_tier == "MINIMAL":
            article = "Art 1"
            article_detail = (
                "Minimal risk — voluntary codes of conduct per Art 69. "
                "No mandatory conformity assessment."
            )

        else:
            article = "Art 43(2)"
            article_detail = (
                "Defaulting to self-assessment per Art 43(2). "
                "Technical documentation must be prepared per Art 11."
            )

        return ConformityPathResult(
            tier=upper_tier,
            conformity_path="NOTIFIED_BODY" if notified_body_required else "SELF_ASSESSMENT",
            article=article,
            article_detail=article_detail,
            notified_body_required=notified_body_required,
            technical_documentation_required=True,
            eu_declaration_conformity_required=True,
        )
