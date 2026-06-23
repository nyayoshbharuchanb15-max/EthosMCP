from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4


class ContextEngine:
    def build_context(self, tool_name: str) -> dict[str, str]:
        return {
            "request_id": str(uuid4()),
            "tool": tool_name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "trust_model": "zero-trust",
            "access_mode": "read-only-metadata",
        }
