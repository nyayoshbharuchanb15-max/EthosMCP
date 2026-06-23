from __future__ import annotations

"""External regulatory API adapters.

This module defines the interface contract that adapter implementations must
satisfy. Each adapter is responsible for querying a single external regulatory
data source (e.g., a national DPA registry, an EU AI Act risk-tier database)
and returning a normalised metadata dict.

**Interface contract** — concrete adapters must return a ``dict`` with at
minimum the following keys:

``status`` (str)
    ``"ok"`` when the upstream source was reachable; ``"unavailable"`` otherwise.
``mode`` (str)
    Must always be ``"read-only"``.  The adapter *must not* mutate the upstream
    source.
``source`` (str)
    Human-readable name of the regulatory data source.
``records`` (list[dict])
    Zero or more normalised records returned by the upstream source.  Each
    record must contain at least ``{"id": str, "jurisdiction": str}``.

**Roadmap** — replace the placeholder below with a concrete HTTP adapter once
upstream API credentials are available. The ``httpx`` package (already in
``pyproject.toml`` / ``requirements.txt``) is the recommended HTTP client.
"""


def fetch_external_regulatory_metadata() -> dict[str, object]:
    """Return regulatory metadata from an external source (placeholder).

    Replace this implementation with a real HTTP call once upstream API
    credentials are provisioned.  The return shape must match the contract
    described in the module docstring.
    """
    return {
        "status": "unavailable",
        "mode": "read-only",
        "source": "placeholder — no upstream configured",
        "records": [],
        "note": "External API adapters are metadata-only placeholders by design.",
    }
