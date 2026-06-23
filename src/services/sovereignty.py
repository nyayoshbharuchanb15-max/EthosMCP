from __future__ import annotations

def query_consent_registry() -> dict[str, str]:
    return {"status": "ok"}


def simulate_dsar_workflow(dsar_request: dict[str, object]) -> dict[str, object]:
    return {"status": "simulated", "request": dsar_request}
