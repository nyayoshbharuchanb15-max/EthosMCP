from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class RiskTier(str, Enum):
    PROHIBITED = "PROHIBITED"
    HIGH = "HIGH"
    LIMITED = "LIMITED"
    MINIMAL = "MINIMAL"

class AuditStatus(str, Enum):
    STARTED = "STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    HALTED = "HALTED"

class RiskClassificationInput(BaseModel):
    system_name: str
    use_case: str
    deployment_context: str
    processes_biometric_data: bool
    used_in_critical_infra: bool
    affects_access_to_services: bool
    autonomous_decision: bool

class RiskTierResult(BaseModel):
    tier: RiskTier
    explanation: str
    regulatory_basis: List[str]
    blocking: bool
    annex_iii_domain: Optional[str] = None

class SupplyChainInput(BaseModel):
    model_id: str
    data_sources: List[str]
    third_party_components: List[str]

class ProvenanceReport(BaseModel):
    ip_risk_score: float
    lineage_complete: bool
    findings: List[str]
    explanation: str
    regulatory_basis: List[str]

class HumanOversightInput(BaseModel):
    architecture_description: str
    has_kill_switch: bool
    override_mechanism: bool
    monitoring_capability: bool
    automation_bias_mitigations: bool

class OversightResult(BaseModel):
    result: str # "PASS" or "BLOCKER_FAIL"
    has_kill_switch: bool
    override_capability: bool
    compliance_status: str
    explanation: str
    regulatory_basis: List[str]
    audit_session_id: Optional[str] = None

class BiasAssessmentInput(BaseModel):
    model_endpoint: str
    test_dataset_ref: str
    protected_classes: List[str]
    intersectional: bool = False

class BiasReport(BaseModel):
    disparity_scores: Dict[str, float]
    findings: List[str]
    worst_performing_group: str
    explanation: str
    regulatory_basis: List[str]

class DPIAInput(BaseModel):
    processing_activity: str
    data_categories: List[str]
    data_subjects: List[str]
    recipients: List[str]
    storage_location: str
    transfer_mechanisms: List[str]

class DPIAReport(BaseModel):
    risk_level: str
    jurisdictional_conflicts: List[str]
    mitigation_measures: List[str]
    explanation: str
    regulatory_basis: List[str]

class AdversarialTestInput(BaseModel):
    model_endpoint: str
    test_suites: List[str]
    threat_model: str

class AdversarialReport(BaseModel):
    robustness_score: float
    attack_surface_map: Dict[str, Any]
    vulnerabilities: List[str]
    explanation: str
    regulatory_basis: List[str]

class WeightedScoreInput(BaseModel):
    audit_session_id: str
    phase_results: List[Dict[str, Any]]

class WeightedAuditScore(BaseModel):
    overall_score: float
    score_breakdown: Dict[str, float]
    compliance_status: str
    blocking: bool
    explanation: str
    regulatory_basis: List[str]

class DriftMonitorInput(BaseModel):
    model_id: str
    production_data_stream: str
    baseline_data_ref: str
    monitoring_thresholds: Dict[str, float]

class DriftAlert(BaseModel):
    drift_detected: bool
    drift_metrics: Dict[str, float]
    threshold_exceeded: List[str]
    reaudit_recommended: bool
    explanation: str
    regulatory_basis: List[str]
