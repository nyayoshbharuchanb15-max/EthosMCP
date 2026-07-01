import { z } from 'zod';
import { zodToJsonSchema } from 'zod-to-json-schema';

// ──────────────────────────────────────────────────
// Shared sub-schemas
// ──────────────────────────────────────────────────

export const UUID = z.string().uuid();
export const SHA256Hex = z.string().length(64).regex(/^[0-9a-f]{64}$/);
export const ISODateTime = z.string().datetime();
export const SemVer = z.string().regex(/^\d+\.\d+\.\d+$/);
export const Email = z.string().email();
export const Jurisdiction = z.enum(['EU', 'IN', 'US', 'UK', 'other']);
export const Severity = z.enum(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL', 'BLOCKER']);
export const PhaseStatus = z.enum(['PASS', 'FAIL', 'BLOCKER']);

export const FindingSchema = z.object({
  finding_id: UUID,
  severity: Severity,
  regulation: z.string(),
  article: z.string(),
  description: z.string().min(1).max(10000),
  remediation: z.string().min(1).max(10000),
});

// ──────────────────────────────────────────────────
// Phase 1 — Register
// ──────────────────────────────────────────────────

export const Phase1InputSchema = z.object({
  system_id: UUID,
  system_name: z.string().min(1).max(200),
  system_version: SemVer,
  vendor: z.string().min(1),
  deployment_environment: z.enum(['production', 'staging', 'development']),
  data_lineage: z.object({
    input_sources: z.array(z.object({
      source_id: z.string(),
      source_type: z.enum(['database', 'api', 'file', 'stream', 'manual']),
      contains_pii: z.boolean(),
      data_subjects: z.array(z.enum(['eu_residents', 'india_residents', 'us_residents', 'other'])),
      legal_basis: z.enum(['consent', 'contract', 'legal_obligation', 'vital_interests', 'public_task', 'legitimate_interests']).optional(),
    })),
    processing_purposes: z.array(z.string().min(1)),
    retention_policy_days: z.number().positive(),
  }).strict(),
  jurisdictions: z.array(Jurisdiction).min(1),
  requested_by: Email,
}).strict();

export const Phase1OutputSchema = z.object({
  run_id: UUID,
  status: z.literal('REGISTERED'),
  phase: z.literal(1),
  timestamp: ISODateTime,
  query_hash: SHA256Hex,
  next_phase: z.literal(2),
});

// ──────────────────────────────────────────────────
// Phase 2 — Scope Regulatory Baseline
// ──────────────────────────────────────────────────

export const Phase2InputSchema = z.object({
  run_id: UUID,
  jurisdictions: z.array(Jurisdiction).min(1),
  system_type: z.string().min(1),
  deployment_context: z.string().min(1),
}).strict();

export const Phase2OutputSchema = z.object({
  run_id: UUID,
  phase: z.literal(2),
  phase_result: PhaseStatus,
  applicable_regulations: z.array(z.string()),
  findings: z.array(FindingSchema),
  artifact_hash: SHA256Hex,
  next_phase: z.literal(3),
});

// ──────────────────────────────────────────────────
// Phase 3 — Risk Classification
// ──────────────────────────────────────────────────

export const Phase3InputSchema = z.object({
  run_id: UUID,
  system_name: z.string().min(1),
  use_case: z.string().min(1),
  deployment_context: z.string().min(1),
  processes_biometric_data: z.boolean(),
  used_in_critical_infra: z.boolean(),
  affects_access_to_services: z.boolean(),
  autonomous_decision: z.boolean(),
  system_type: z.string().optional(),
}).strict();

export const Phase3OutputSchema = z.object({
  run_id: UUID,
  phase: z.literal(3),
  phase_result: PhaseStatus,
  tier: z.enum(['UNACCEPTABLE', 'HIGH', 'LIMITED', 'MINIMAL']),
  conformity_path: z.enum(['SELF_ASSESSMENT', 'NOTIFIED_BODY']),
  annex_reference: z.string().optional(),
  findings: z.array(FindingSchema),
  artifact_hash: SHA256Hex,
  next_phase: z.literal(4),
});

// ──────────────────────────────────────────────────
// Phase 4 — Privacy Compliance
// ──────────────────────────────────────────────────

export const Phase4InputSchema = z.object({
  run_id: UUID,
  processing_activity: z.string().min(1),
  data_categories: z.array(z.string()).min(1),
  data_subjects: z.array(z.string()).min(1),
  recipients: z.array(z.string()).min(1),
  storage_location: z.string().min(1),
  transfer_mechanisms: z.array(z.string()),
  cross_border_transfer: z.boolean(),
}).strict();

export const Phase4OutputSchema = z.object({
  run_id: UUID,
  phase: z.literal(4),
  phase_result: PhaseStatus,
  risk_level: z.enum(['LOW', 'MEDIUM', 'HIGH']),
  jurisdictional_conflicts: z.array(z.string()),
  mitigation_measures: z.array(z.string()),
  findings: z.array(FindingSchema),
  artifact_hash: SHA256Hex,
  next_phase: z.literal(5),
});

// ──────────────────────────────────────────────────
// Phase 5 — Bias Assessment
// ──────────────────────────────────────────────────

export const Phase5InputSchema = z.object({
  run_id: UUID,
  model_endpoint: z.string().url().optional(),
  test_dataset_ref: z.string().min(1),
  protected_classes: z.array(z.string()).min(1),
  intersectional: z.boolean(),
  y_true_path: z.string().optional(),
  y_pred_path: z.string().optional(),
}).strict();

export const Phase5OutputSchema = z.object({
  run_id: UUID,
  phase: z.literal(5),
  phase_result: PhaseStatus,
  disparity_scores: z.record(z.number().min(0).max(1)),
  worst_performing_group: z.string(),
  findings: z.array(FindingSchema),
  artifact_hash: SHA256Hex,
  next_phase: z.literal(6),
});

// ──────────────────────────────────────────────────
// Phase 6 — Security Tests
// ──────────────────────────────────────────────────

export const Phase6InputSchema = z.object({
  run_id: UUID,
  model_endpoint: z.string().url().optional(),
  test_suites: z.array(z.string()).min(1),
  threat_model: z.string().min(1),
  model_type: z.enum(['classifier', 'generative', 'regression']).optional(),
}).strict();

export const Phase6OutputSchema = z.object({
  run_id: UUID,
  phase: z.literal(6),
  phase_result: PhaseStatus,
  robustness_score: z.number().min(0).max(100),
  attack_surface_map: z.record(z.string()),
  vulnerabilities: z.array(z.string()),
  findings: z.array(FindingSchema),
  artifact_hash: SHA256Hex,
  next_phase: z.literal(7),
});

// ──────────────────────────────────────────────────
// Phase 7 — Explainability Report
// ──────────────────────────────────────────────────

export const Phase7InputSchema = z.object({
  run_id: UUID,
  model_endpoint: z.string().url().optional(),
  explainability_method: z.enum(['shap', 'lime', 'both']),
  sample_count: z.number().positive().max(10000).optional(),
  feature_names: z.array(z.string()).optional(),
}).strict();

export const Phase7OutputSchema = z.object({
  run_id: UUID,
  phase: z.literal(7),
  phase_result: PhaseStatus,
  method_used: z.enum(['shap', 'lime', 'both']),
  global_feature_importance: z.record(z.number()),
  findings: z.array(FindingSchema),
  artifact_hash: SHA256Hex,
  next_phase: z.literal(8),
});

// ──────────────────────────────────────────────────
// Phase 8 — Certificate Issuance
// ──────────────────────────────────────────────────

export const Phase8InputSchema = z.object({
  run_id: UUID,
  verify_all_phases_passed: z.boolean(),
}).strict();

export const Phase8OutputSchema = z.object({
  run_id: UUID,
  phase: z.literal(8),
  phase_result: PhaseStatus,
  certification_issued: z.boolean(),
  vc_json: z.any().optional(),
  proof_value: z.string().optional(),
  merkle_root: SHA256Hex.optional(),
  timestamp_token: z.string().optional(),
  findings: z.array(FindingSchema),
  artifact_hash: SHA256Hex,
  next_phase: z.literal(9),
});

// ──────────────────────────────────────────────────
// Phase 9 — Drift Monitoring
// ──────────────────────────────────────────────────

export const Phase9InputSchema = z.object({
  run_id: UUID,
  model_id: z.string().min(1),
  production_data_stream: z.string().min(1),
  baseline_data_ref: z.string().min(1),
  monitoring_thresholds: z.record(z.number()),
}).strict();

export const Phase9OutputSchema = z.object({
  run_id: UUID,
  phase: z.literal(9),
  phase_result: PhaseStatus,
  drift_detected: z.boolean(),
  drift_metrics: z.record(z.number()),
  threshold_exceeded: z.array(z.string()),
  reaudit_recommended: z.boolean(),
  findings: z.array(FindingSchema),
  artifact_hash: SHA256Hex,
  monitoring_id: z.string().uuid(),
});

// ──────────────────────────────────────────────────
// Export Zod-to-JSON Schema wrappers for MCP tool registration
// ──────────────────────────────────────────────────

export const inputSchemas = {
  phase1: Phase1InputSchema,
  phase2: Phase2InputSchema,
  phase3: Phase3InputSchema,
  phase4: Phase4InputSchema,
  phase5: Phase5InputSchema,
  phase6: Phase6InputSchema,
  phase7: Phase7InputSchema,
  phase8: Phase8InputSchema,
  phase9: Phase9InputSchema,
};

export function getJsonSchema(phase: number) {
  const key = `phase${phase}` as keyof typeof inputSchemas;
  return zodToJsonSchema(inputSchemas[key], {
    $refStrategy: 'none',
    target: 'openApi3',
  });
}
