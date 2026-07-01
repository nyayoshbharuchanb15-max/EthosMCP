import crypto from 'node:crypto';
import axios from 'axios';
import { Phase5InputSchema, Phase5OutputSchema, type Finding } from '../types/schemas.js';
import { logger } from '../index.js';

const ORCHESTRATOR_URL = process.env.ORCHESTRATOR_URL || 'http://localhost:8080';

// Standard fairness thresholds per EU AI Act Art. 10(2)(f) and NIST
const METRIC_THRESHOLDS: Record<string, number> = {
  demographic_parity_difference: 0.10,
  equalized_odds_difference: 0.10,
  equal_opportunity_difference: 0.10,
  disparate_impact_ratio: 0.80,
};

export async function runBiasAssessment(input: any) {
  const parsed = Phase5InputSchema.parse(input);
  const { run_id, protected_classes, intersectional } = parsed;

  const disparity_scores: Record<string, number> = {};
  const findings: Finding[] = [];

  // Simulate bias metrics for each protected class
  for (const cls of protected_classes) {
    let score: number;
    if (cls === 'race') {
      score = 0.12;
    } else if (cls === 'gender' || cls === 'sex') {
      score = 0.08;
    } else if (intersectional && cls.includes('race_')) {
      score = 0.15;
    } else {
      score = 0.04 + Math.random() * 0.04;
    }
    disparity_scores[cls] = score;
  }

  let worstGroup = '';
  let worstScore = 0;
  for (const [cls, score] of Object.entries(disparity_scores)) {
    if (score > worstScore) {
      worstScore = score;
      worstGroup = cls;
    }

    if (score > METRIC_THRESHOLDS.demographic_parity_difference) {
      const severity = score > METRIC_THRESHOLDS.demographic_parity_difference * 2 ? 'BLOCKER' : 'HIGH';
      findings.push({
        finding_id: crypto.randomUUID(),
        severity,
        regulation: 'EU AI Act',
        article: 'Art. 10(2)(f) / Annex IV §2(d)',
        description: `Demographic parity difference for "${cls}" is ${(score * 100).toFixed(1)}%, exceeding threshold of ${(METRIC_THRESHOLDS.demographic_parity_difference * 100)}%`,
        remediation: 'Retrain with reweighted samples, apply post-processing fairness constraint (e.g., reject option classification), or collect more representative training data',
      });
    }
  }

  if (intersectional && protected_classes.length >= 2) {
    const intersectionalScore = worstScore * 1.2;
    if (intersectionalScore > METRIC_THRESHOLDS.demographic_parity_difference) {
      findings.push({
        finding_id: crypto.randomUUID(),
        severity: 'HIGH',
        regulation: 'EU AI Act',
        article: 'Art. 10(3)',
        description: `Intersectional bias detected — combined disparity for multiple protected attributes is ${(intersectionalScore * 100).toFixed(1)}%`,
        remediation: 'Perform intersectional fairness analysis across combined protected attribute groups per Art. 10(3) requirements',
      });
    }
  }

  const canonical = JSON.stringify(parsed, Object.keys(parsed).sort());
  const artifact_hash = crypto.createHash('sha256').update(canonical).digest('hex');

  try {
    await axios.post(`${ORCHESTRATOR_URL}/audit/bias`, parsed, { timeout: 10000 });
  } catch (error: any) {
    logger.warn('Bias assessment sync failed', { run_id, error: error.message });
  }

  const phase_result = findings.some(f => f.severity === 'BLOCKER') ? 'BLOCKER' : 'PASS';

  const output = Phase5OutputSchema.parse({
    run_id,
    phase: 5,
    phase_result,
    disparity_scores,
    worst_performing_group: worstGroup,
    findings,
    artifact_hash,
    next_phase: 6,
  });

  return { content: [{ type: 'text', text: JSON.stringify(output, null, 2) }] };
}
