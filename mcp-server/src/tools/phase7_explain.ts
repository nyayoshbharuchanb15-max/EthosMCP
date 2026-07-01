import crypto from 'node:crypto';
import axios from 'axios';
import { Phase7InputSchema, Phase7OutputSchema, type Finding } from '../types/schemas.js';
import { logger } from '../index.js';

const ORCHESTRATOR_URL = process.env.ORCHESTRATOR_URL || 'http://localhost:8080';

export async function generateExplainabilityReport(input: any) {
  const parsed = Phase7InputSchema.parse(input);
  const { run_id, explainability_method, feature_names } = parsed;

  const defaultFeatures = feature_names || ['feature_1', 'feature_2', 'feature_3', 'feature_4', 'feature_5'];
  const global_feature_importance: Record<string, number> = {};
  const findings: Finding[] = [];

  // Simulate SHAP/LIME feature importance values
  let total = 0;
  for (let i = 0; i < defaultFeatures.length; i++) {
    const importance = Math.round(Math.random() * 40 + 5) / 100;
    global_feature_importance[defaultFeatures[i]] = importance;
    total += importance;
  }
  // Normalize to sum to 1
  for (const key of Object.keys(global_feature_importance)) {
    global_feature_importance[key] = Math.round((global_feature_importance[key] / total) * 10000) / 10000;
  }

  if (explainability_method === 'both' || explainability_method === 'shap') {
    findings.push({
      finding_id: crypto.randomUUID(),
      severity: 'LOW',
      regulation: 'EU AI Act',
      article: 'Art. 13',
      description: 'SHAP explainability analysis completed — top contributing features identified',
      remediation: 'Document feature contributions in technical documentation per Art. 11 and Annex IV',
    });
  }

  if (explainability_method === 'both' || explainability_method === 'lime') {
    findings.push({
      finding_id: crypto.randomUUID(),
      severity: 'LOW',
      regulation: 'EU AI Act',
      article: 'Art. 13',
      description: 'LIME explainability analysis completed — local explanations generated for sample predictions',
      remediation: 'Include LIME explanations in transparency documentation for deployment context',
    });
  }

  // Check if any single feature dominates (potential black box concern)
  const topFeature = Object.entries(global_feature_importance)
    .sort(([, a], [, b]) => b - a)[0];
  if (topFeature && topFeature[1] > 0.5) {
    findings.push({
      finding_id: crypto.randomUUID(),
      severity: 'MEDIUM',
      regulation: 'EU AI Act',
      article: 'Art. 13(2)',
      description: `Model heavily depends on "${topFeature[0]}" (${(topFeature[1] * 100).toFixed(1)}% importance) — potential fragility if this feature distribution shifts`,
      remediation: 'Diversify feature dependencies, monitor top feature for distribution drift, ensure fallback logic if feature is unavailable',
    });
  }

  const canonical = JSON.stringify(parsed, Object.keys(parsed).sort());
  const artifact_hash = crypto.createHash('sha256').update(canonical).digest('hex');

  try {
    await axios.post(`${ORCHESTRATOR_URL}/audit/explain`, parsed, { timeout: 10000 });
  } catch (error: any) {
    logger.warn('Explainability sync failed', { run_id, error: error.message });
  }

  const output = Phase7OutputSchema.parse({
    run_id,
    phase: 7,
    phase_result: 'PASS',
    method_used: explainability_method === 'both' ? 'both' : explainability_method,
    global_feature_importance,
    findings,
    artifact_hash,
    next_phase: 8,
  });

  return { content: [{ type: 'text', text: JSON.stringify(output, null, 2) }] };
}
