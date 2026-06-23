from __future__ import annotations


def fetch_external_regulatory_metadata() -> dict[str, str]:
    return {
        "status": "unqueried",
        "mode": "read-only",
        "note": "External API adapters are metadata-only placeholders by design.",
    }
