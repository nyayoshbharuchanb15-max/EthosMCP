import crypto from 'node:crypto';
import axios from 'axios';
import { Phase2InputSchema, Phase2OutputSchema, type Finding } from '../types/schemas.js';
import { logger } from '../index.js';

const ORCHESTRATOR_URL = process.env.ORCHESTRATOR_URL || 'http://localhost:8080';

const REGULATORY_FRAMEWORKS: Record<string, string[]> = {
  EU: ['EU AI Act', 'GDPR'],
  IN: ['DPDP Act', 'IT Act'],
  US: ['State AI Laws', 'FTC Guidelines'],
  UK: ['UK AI Regulation', 'UK GDPR'],
  other: ['Local regulations'],
};

export async function scopeRegulatoryBaseline(input: any) {
  const parsed = Phase2InputSchema.parse(input);
  const { run_id, jurisdictions, system_type, deployment_context } = parsed;

  const applicable: string[] = [];
  const findings: Finding[] = [];

  for (const j of jurisdictions) {
    const frameworks = REGULATORY_FRAMEWORKS[j] || [];
    applicable.push(...frameworks);
  }

  if (system_type.toLowerCase().includes('biometric') || system_type.toLowerCase().includes('facial')) {
    findings.push({
      finding_id: crypto.randomUUID(),
      severity: 'HIGH',
      regulation: 'EU AI Act',
      article: 'Annex III §1',
      description: 'Biometric identification system triggers notified-body conformity assessment',
      remediation: 'Prepare technical documentation per Art. 11 and engage notified body',
    });
  }

  if (jurisdictions.includes('IN')) {
    findings.push({
      finding_id: crypto.randomUUID(),
      severity: 'MEDIUM',
      regulation: 'DPDP Act',
      article: 'Sec. 8-9',
      description: 'Data Fiduciary obligations apply; check if Significant Data Fiduciary',
      remediation: 'Register with DPDP Authority if processing large volumes of personal data',
    });
  }

  const canonical = JSON.stringify(parsed, Object.keys(parsed).sort());
  const artifact_hash = crypto.createHash('sha256').update(canonical).digest('hex');

  try {
    await axios.post(`${ORCHESTRATOR_URL}/audit/scope`, parsed, { timeout: 10000 });
  } catch (error: any) {
    logger.warn('Scope sync to orchestrator failed, continuing', { run_id, error: error.message });
  }

  const output = Phase2OutputSchema.parse({
    run_id,
    phase: 2,
    phase_result: findings.some(f => f.severity === 'BLOCKER') ? 'BLOCKER' : 'PASS',
    applicable_regulations: [...new Set(applicable)],
    findings,
    artifact_hash,
    next_phase: 3,
  });

  return { content: [{ type: 'text', text: JSON.stringify(output, null, 2) }] };
}
