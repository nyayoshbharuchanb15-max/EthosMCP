from __future__ import annotations

from enum import Enum

class EuAiActRiskTier(str, Enum):
    UNACCEPTABLE = "UNACCEPTABLE"
    HIGH_RISK = "HIGH_RISK"
    LIMITED_RISK = "LIMITED_RISK"
    MINIMAL_RISK = "MINIMAL_RISK"


def classify_risk(*, prohibited: bool = False, annex_iii: bool = False, transparency: bool = False) -> EuAiActRiskTier:
    if prohibited:
        return EuAiActRiskTier.UNACCEPTABLE
    if annex_iii:
        return EuAiActRiskTier.HIGH_RISK
    if transparency:
        return EuAiActRiskTier.LIMITED_RISK
    return EuAiActRiskTier.MINIMAL_RISK
