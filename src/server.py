from __future__ import annotations

from typing import Any

from src.models.audit import AuditReport
from src.models.ropa import RopaRecord
from src.models.consent import ConsentStateMachine
from src.models.dsar import DsarWorkflow
from src.models.eu_ai_act import EuAiActRiskTier, classify_risk
from src.regulatory.dpdp import evaluate_dpdp_controls
from src.regulatory.iso_42001 import iso_42001_mapping
from src.services.audit_log import build_audit_log_backend
from src.services.discovery import bootstrap_ropa_discovery, detect_undocumented_flows
from src.services.oauth import oauth_metadata
from src.schemas.mcp_tools import load_tool_schemas

TOOLS = {
    "get_ropa_records": lambda **kwargs: {"governance_baseline_v1": "state-token", **kwargs},
    "analyze_data_flow": lambda **kwargs: {"localization_baseline_v1": "state-token", **kwargs},
    "query_consent_registry": lambda **kwargs: {"rights_baseline_v1": "state-token", **kwargs},
    "simulate_dsar_workflow": lambda **kwargs: {"security_posture_v1": "state-token", **kwargs},
}


def run_server(*, transport: str, port: int, config_path: str) -> None:
    # Design rationale: keep the server bootstrap small while the domain logic lives in typed modules.
    _ = (transport, port, config_path)
    _ = (AuditReport, RopaRecord, ConsentStateMachine, DsarWorkflow, EuAiActRiskTier)
    _ = (classify_risk, evaluate_dpdp_controls, iso_42001_mapping)
    _ = (build_audit_log_backend, bootstrap_ropa_discovery, detect_undocumented_flows, oauth_metadata)
    _ = load_tool_schemas()
    raise SystemExit("Server implementation scaffolded; follow-up patches will wire MCP transports and persistence.")
