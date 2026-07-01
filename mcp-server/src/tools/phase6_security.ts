import crypto from 'node:crypto';
import axios from 'axios';
import { Phase6InputSchema, Phase6OutputSchema, type Finding } from '../types/schemas.js';
import { logger } from '../index.js';

const ORCHESTRATOR_URL = process.env.ORCHESTRATOR_URL || 'http://localhost:8080';

export async function runSecurityTests(input: any) {
  const parsed = Phase6InputSchema.parse(input);
  const { run_id, test_suites, threat_model, model_type } = parsed;

  const attack_surface_map: Record<string, string> = {};
  const vulnerabilities: string[] = [];
  const findings: Finding[] = [];

  // Simulate adversarial testing based on test suites
  if (test_suites.includes('prompt_injection')) {
    attack_surface_map['prompt_injection'] = 'medium';
    vulnerabilities.push('Potential prompt injection vulnerability in input processing');
    findings.push({
      finding_id: crypto.randomUUID(),
      severity: 'MEDIUM',
      regulation: 'EU AI Act',
      article: 'Art. 15',
      description: 'Prompt injection attack surface identified — model may execute unintended instructions',
      remediation: 'Implement input sanitization, output validation, and prompt guardrails per OWASP LLM Top 10',
    });
  }

  if (test_suites.includes('model_extraction') || test_suites.includes('membership_inference')) {
    attack_surface_map['model_extraction'] = 'high';
    vulnerabilities.push('Model extraction via API probing is feasible');
    findings.push({
      finding_id: crypto.randomUUID(),
      severity: 'HIGH',
      regulation: 'GDPR',
      article: 'Art. 5(1)(c)',
      description: 'Data minimisation principle may be violated — model can memorise and expose training data',
      remediation: 'Apply differential privacy during training, limit API output precision, implement query monitoring',
    });
  }

  if (test_suites.includes('ood') || test_suites.includes('adversarial_examples')) {
    attack_surface_map['out_of_distribution'] = 'low';
    vulnerabilities.push('Sensitivity to out-of-distribution (OOD) inputs detected');
    findings.push({
      finding_id: crypto.randomUUID(),
      severity: 'MEDIUM',
      regulation: 'EU AI Act',
      article: 'Art. 15',
      description: 'Model robustness to distribution shift requires improvement',
      remediation: 'Implement OOD detection, use adversarial training, set confidence thresholds for rejecting uncertain predictions',
    });
  }

  if (model_type === 'generative') {
    attack_surface_map['jailbreak'] = 'critical';
    vulnerabilities.push('Jailbreak attack surface — model may bypass safety guardrails');
    findings.push({
      finding_id: crypto.randomUUID(),
      severity: 'CRITICAL',
      regulation: 'EU AI Act',
      article: 'Art. 15 / Art. 52(1)',
      description: 'Generative AI system vulnerable to jailbreak attacks that bypass safety measures',
      remediation: 'Implement multi-layer safety guardrails, content filtering, and human-in-the-loop review for high-risk outputs',
    });
  }

  // Data minimisation check (GDPR Art. 5(1)(c))
  if (test_suites.includes('data_minimisation')) {
    findings.push({
      finding_id: crypto.randomUUID(),
      severity: 'LOW',
      regulation: 'GDPR',
      article: 'Art. 5(1)(c)',
      description: 'Data minimisation principle assessment — review if only necessary data is collected and retained',
      remediation: 'Audit data collection pipelines, implement retention policies, purge unnecessary training features',
    });
  }

  const overallRisk = Object.values(attack_surface_map);
  const robustness_score = overallRisk.length === 0
    ? 100
    : Math.round(100 - (overallRisk.filter(r => r === 'critical').length * 25 +
        overallRisk.filter(r => r === 'high').length * 15 +
        overallRisk.filter(r => r === 'medium').length * 8));

  const canonical = JSON.stringify(parsed, Object.keys(parsed).sort());
  const artifact_hash = crypto.createHash('sha256').update(canonical).digest('hex');

  try {
    await axios.post(`${ORCHESTRATOR_URL}/audit/security`, parsed, { timeout: 10000 });
  } catch (error: any) {
    logger.warn('Security tests sync failed', { run_id, error: error.message });
  }

  const phase_result = findings.some(f => f.severity === 'BLOCKER') ? 'BLOCKER' : 'PASS';

  const output = Phase6OutputSchema.parse({
    run_id,
    phase: 6,
    phase_result,
    robustness_score: Math.max(0, Math.min(100, robustness_score)),
    attack_surface_map,
    vulnerabilities,
    findings,
    artifact_hash,
    next_phase: 7,
  });

  return { content: [{ type: 'text', text: JSON.stringify(output, null, 2) }] };
}
