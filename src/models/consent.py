from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum

class ConsentState(str, Enum):
    NEVER_ASKED = "NEVER_ASKED"
    PENDING = "PENDING"
    GRANTED = "GRANTED"
    WITHDRAWN = "WITHDRAWN"
    EXPIRED = "EXPIRED"
    REVOKED_BY_REGULATION = "REVOKED_BY_REGULATION"

@dataclass(frozen=True)
class ConsentEvent:
    from_state: ConsentState
    to_state: ConsentState
    timestamp: datetime
    legal_basis_reference: str
    notice_language: str | None = None

@dataclass
class ConsentStateMachine:
    state: ConsentState = ConsentState.NEVER_ASKED
    events: list[ConsentEvent] = field(default_factory=list)

    def transition(self, to_state: ConsentState, legal_basis_reference: str, notice_language: str | None = None) -> None:
        # Design rationale: an immutable event stream preserves the audit history of consent changes.
        event = ConsentEvent(self.state, to_state, datetime.now(timezone.utc), legal_basis_reference, notice_language)
        self.events.append(event)
        self.state = to_state
