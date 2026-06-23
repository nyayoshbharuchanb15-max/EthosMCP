from __future__ import annotations

from enum import Enum

class Iso42001Control(str, Enum):
    CLAUSE_4_1 = "Clause 4.1"
    CLAUSE_6_1_2 = "Clause 6.1.2"
    CLAUSE_8_4 = "Clause 8.4"
    CLAUSE_9_1 = "Clause 9.1"
    CLAUSE_10_1 = "Clause 10.1"

iso_42001_mapping: dict[str, str] = {
    "Phase 1 ROPA checks": Iso42001Control.CLAUSE_4_1.value,
    "EU AI Act risk tier classification": Iso42001Control.CLAUSE_6_1_2.value,
    "Phase 3 DSAR simulation": Iso42001Control.CLAUSE_8_4.value,
    "Phase 4 security posture": Iso42001Control.CLAUSE_9_1.value,
    "Remediation verification workflow": Iso42001Control.CLAUSE_10_1.value,
}
