from __future__ import annotations

"""Compliance control knowledge-graph connectors.

This module defines the interface contract for knowledge-graph adapters that
surface the control relationships between regulatory frameworks, audit phases,
and organisational data assets.

**Interface contract** — implementations must return a ``dict`` that matches:

``graph`` (str)
    Identifier of the knowledge graph (e.g. ``"compliance-controls"``).
``mode`` (str)
    Must always be ``"read-only"``.  The connector *must not* write to the graph.
``nodes`` (list[str])
    Top-level control domain nodes present in the snapshot.
``edges`` (list[dict])
    Directed edges representing dependency or coverage relationships.  Each
    edge must contain ``{"from": str, "to": str, "relationship": str}``.

**Roadmap** — replace the placeholder below with a connector to a production
graph store (e.g. Neo4j via ``neo4j`` driver, or a SPARQL endpoint) once the
ontology schema is finalised.
"""


def get_control_graph_snapshot() -> dict[str, object]:
    """Return a snapshot of the compliance-control knowledge graph (placeholder).

    Replace this implementation with a real graph query once a graph store is
    provisioned.  The return shape must match the contract described in the
    module docstring.
    """
    return {
        "graph": "compliance-controls",
        "mode": "read-only",
        "nodes": ["governance", "localization", "sovereignty", "security"],
        "edges": [
            {"from": "governance", "to": "localization", "relationship": "precedes"},
            {"from": "localization", "to": "sovereignty", "relationship": "precedes"},
            {"from": "sovereignty", "to": "security", "relationship": "precedes"},
        ],
    }
