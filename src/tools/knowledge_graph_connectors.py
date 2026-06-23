from __future__ import annotations


def get_control_graph_snapshot() -> dict[str, object]:
    return {
        "graph": "compliance-controls",
        "mode": "read-only",
        "nodes": ["governance", "localization", "sovereignty", "security"],
    }
