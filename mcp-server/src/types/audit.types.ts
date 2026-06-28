import { ExplainableResult } from './regulatory.types';

export interface ProvenanceReport extends ExplainableResult {
  ip_risk_score: number;
  lineage_complete: boolean;
  findings: string[];
}

export interface OversightCertificate extends ExplainableResult {
  has_kill_switch: boolean;
  override_capability: boolean;
  compliance_status: 'Compliant' | 'Non-Compliant';
}

export interface BiasReport extends ExplainableResult {
  disparity_scores: Record<string, number>;
  findings: string[];
  worst_performing_group: string;
}

export interface DPIAReport extends ExplainableResult {
  risk_level: 'Low' | 'Medium' | 'High';
  jurisdictional_conflicts: string[];
  mitigation_measures: string[];
}

export interface AdversarialReport extends ExplainableResult {
  robustness_score: number;
  attack_surface_map: Record<string, any>;
  vulnerabilities: string[];
}

export interface WeightedAuditScore extends ExplainableResult {
  overall_score: number;
  score_breakdown: Record<string, number>;
  compliance_status: 'Compliant' | 'Non-Compliant';
  blocking: boolean;
}

export interface FailNotice extends ExplainableResult {
  fail_notice_id: string;
  audit_session_id: string;
  reason: string;
  details: string;
  issued_at: string;
}
