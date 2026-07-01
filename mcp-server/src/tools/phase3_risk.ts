import crypto from 'node:crypto';
import axios from 'axios';
import { Phase3InputSchema, Phase3OutputSchema, type Finding } from '../types/schemas.js';
import { logger } from '../index.js';

const ORCHESTRATOR_URL = process.env.ORCHESTRATOR_URL || 'http://localhost:8080';

const PROHIBITED_USE_CASES = [
  'subliminal manipulation', 'social scoring', 'real-time remote biometric',
  'emotion recognition workplace', 'biometric categorisation sensitive',
  'predictive policing individual',
];

const ANNEX_III_DOMAINS: Record<string, string> = {
  biometric: 'Annex III §1',
  'critical infrastructure': 'Annex III §2',
  education: 'Annex III §3',
  employment: 'Annex III §4',
  'essential services': 'Annex III §5',
  'law enforcement': 'Annex III §6',
  migration: 'Annex III §7',
  justice: 'Annex III §8',
};

export async function classifyAiRisk(input: any) {
  const parsed = Phase3InputSchema.parse(input);
  const { run_id, use_case, deployment_context, processes_biometric_data,
    used_in_critical_infra, affects_access_to_services, autonomous_decision } = parsed;

  const findings: Finding[] = [];
  let tier: string;
  let conformity_path: string;
  let annex_reference: string | undefined;

  const useCaseLower = use_case.toLowerCase();
  const ctxLower = deployment_context.toLowerCase();

  // Check prohibited (Art 5)
  const isProhibited = PROHIBITED_USE_CASES.some(p => useCaseLower.includes(p)) ||
    (processes_biometric_data && autonomous_decision);

  if (isProhibited) {
    tier = 'UNACCEPTABLE';
    conformity_path = 'NOTIFIED_BODY';
    findings.push({
      finding_id: crypto.randomUUID(),
      severity: 'BLOCKER',
      regulation: 'EU AI Act',
      article: 'Art. 5',
      description: 'System falls under prohibited AI practices — cannot be deployed in the EU',
      remediation: 'Redesign system to eliminate prohibited characteristics per Art. 5(1)-(6)',
    });
  } else if (used_in_critical_infra || affects_access_to_services ||
    ctxLower.includes('law enforcement') || ctxLower.includes('education') ||
    processes_biometric_data) {
    tier = 'HIGH';
    conformity_path = processes_biometric_data ? 'NOTIFIED_BODY' : 'SELF_ASSESSMENT';

    for (const [domain, ref] of Object.entries(ANNEX_III_DOMAINS)) {
      if (ctxLower.includes(domain) || useCaseLower.includes(domain)) {
        annex_reference = ref;
        break;
      }
    }
    if (!annex_reference) annex_reference = 'Annex III §5';

    findings.push({
      finding_id: crypto.randomUUID(),
      severity: 'HIGH',
      regulation: 'EU AI Act',
      article: `${annex_reference}`,
      description: `High-risk AI system under ${annex_reference} requiring conformity assessment`,
      remediation: 'Prepare technical documentation per Art. 11, implement risk management per Art. 9',
    });
  } else if (useCaseLower.includes('chatbot') || useCaseLower.includes('emotion')) {
    tier = 'LIMITED';
    conformity_path = 'SELF_ASSESSMENT';
    findings.push({
      finding_id: crypto.randomUUID(),
      severity: 'MEDIUM',
      regulation: 'EU AI Act',
      article: 'Art. 52',
      description: 'Limited risk AI system requires transparency obligations',
      remediation: 'Implement disclosure that users are interacting with AI per Art. 52(1)',
    });
  } else {
    tier = 'MINIMAL';
    conformity_path = 'SELF_ASSESSMENT';
  }

  const canonical = JSON.stringify(parsed, Object.keys(parsed).sort());
  const artifact_hash = crypto.createHash('sha256').update(canonical).digest('hex');

  try {
    await axios.post(`${ORCHESTRATOR_URL}/audit/classify`, parsed, { timeout: 10000 });
  } catch (error: any) {
    logger.warn('Risk classification sync failed', { run_id, error: error.message });
  }

  const phase_result = findings.some(f => f.severity === 'BLOCKER') ? 'BLOCKER' : 'PASS';

  const output = Phase3OutputSchema.parse({
    run_id,
    phase: 3,
    phase_result,
    tier,
    conformity_path,
    annex_reference,
    findings,
    artifact_hash,
    next_phase: 4,
  });

  return { content: [{ type: 'text', text: JSON.stringify(output, null, 2) }] };
}
