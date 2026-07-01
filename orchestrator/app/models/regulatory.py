from pydantic import BaseModel, Field
from typing import Literal


class RegulatoryScope(BaseModel):
    jurisdiction: str
    frameworks: list[str]
    articles: list[str]


class ConformityPath(BaseModel):
    tier: Literal["UNACCEPTABLE", "HIGH", "LIMITED", "MINIMAL"]
    path: Literal["SELF_ASSESSMENT", "NOTIFIED_BODY"]
    article: str = Field(..., description="EU AI Act article reference")
    notified_body_required: bool = False


class AnnexIIICategory(BaseModel):
    id: str
    category: str
    article: str
    conformity_required: Literal["self_assessment", "notified_body"]
    prohibited_subset: list[str] = Field(default_factory=list)
