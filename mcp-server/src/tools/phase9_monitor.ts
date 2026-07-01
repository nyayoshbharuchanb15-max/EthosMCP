import crypto from 'node:crypto';
import axios from 'axios';
import { Phase9InputSchema, Phase9OutputSchema, type Finding } from '../types/schemas.js';
import { logger } from '../index.js';

const ORCHESTRATOR_URL = process.env.ORCHESTRATOR_URL || 'http://localhost:8080';

export async function monitorModelDrift(input: any) {
  const parsed = Phase9InputSchema.parse(input);
  const { run_id, model_id, production_data_stream, baseline_data_ref, monitoring_thresholds } = parsed;

  const findings: Finding[] = [];
  const drift_metrics: Record<string, number> = {};
  const threshold_exceeded: string[] = [];

  // Simulate drift detection
  for (const [metric, threshold] of Object.entries(monitoring_thresholds)) {
    const simulatedValue = Math.random() * (threshold * 1.5);
    drift_metrics[metric] = Math.round(simulatedValue * 10000) / 10000;

    if (simulatedValue > threshold) {
      threshold_exceeded.push(metric);
      const severity = simulatedValue > threshold * 1.5 ? 'HIGH' : 'MEDIUM';
      findings.push({
        finding_id: crypto.randomUUID(),
        severity,
        regulation: 'EU AI Act',
        article: 'Art. 35 / ISO 42001 Clause 8',
        description: `Drift detected in "${metric}": ${(simulatedValue * 100).toFixed(2)}% exceeds threshold of ${(threshold * 100).toFixed(2)}%`,
        remediation: 'Investigate root cause of drift, consider model retraining, evaluate impact on fairness metrics',
      });
    }
  }

  if (findings.length > 0) {
    logger.warn('Drift detected', { model_id, exceeded_metrics: threshold_exceeded, run_id });
  }

  const reaudit_recommended = threshold_exceeded.length > 0;

  if (reaudit_recommended) {
    try {
      await axios.post(`${ORCHESTRATOR_URL}/audit/reaudit`, {
        run_id,
        model_id,
        changed_components: threshold_exceeded,
      }, { timeout: 10000 });
      logger.info('Reaudit trigger sent', { run_id, changed_components: threshold_exceeded });
    } catch (error: any) {
      logger.warn('Reaudit trigger failed', { run_id, error: error.message });
    }
  }

  const canonical = JSON.stringify(parsed, Object.keys(parsed).sort());
  const artifact_hash = crypto.createHash('sha256').update(canonical).digest('hex');

  const output = Phase9OutputSchema.parse({
    run_id,
    phase: 9,
    phase_result: findings.some(f => f.severity === 'BLOCKER') ? 'BLOCKER' : 'PASS',
    drift_detected: threshold_exceeded.length > 0,
    drift_metrics,
    threshold_exceeded,
    reaudit_recommended,
    findings,
    artifact_hash,
    monitoring_id: crypto.randomUUID(),
  });

  return { content: [{ type: 'text', text: JSON.stringify(output, null, 2) }] };
}
