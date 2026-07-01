import crypto from 'node:crypto';
import axios from 'axios';
import { Phase4InputSchema, Phase4OutputSchema, type Finding } from '../types/schemas.js';
import { logger } from '../index.js';

const ORCHESTRATOR_URL = process.env.ORCHESTRATOR_URL || 'http://localhost:8080';

export async function assessPrivacyCompliance(input: any) {
  const parsed = Phase4InputSchema.parse(input);
  const { run_id, processing_activity, data_categories, data_subjects, recipients,
    storage_location, transfer_mechanisms, cross_border_transfer } = parsed;

  const findings: Finding[] = [];
  const jurisdictional_conflicts: string[] = [];
  const mitigation_measures: string[] = [];

  let risk_level: 'LOW' | 'MEDIUM' | 'HIGH';

  // GDPR Art. 35 DPIA assessment
  if (data_subjects.some(s => ['health', 'biometric', 'genetic', 'criminal'].includes(s.toLowerCase()))) {
    risk_level = 'HIGH';
    findings.push({
      finding_id: crypto.randomUUID(),
      severity: 'HIGH',
      regulation: 'GDPR',
      article: 'Art. 35(3)',
      description: 'Processing of special category data requires mandatory DPIA',
      remediation: 'Perform full DPIA per Art. 35(7) including systematic description, necessity assessment, and risk mitigation measures',
    });
  } else if (cross_border_transfer) {
    risk_level = 'HIGH';
    jurisdictional_conflicts.push(`Data stored in ${storage_location} with cross-border transfer to ${recipients.join(', ')}`);
    findings.push({
      finding_id: crypto.randomUUID(),
      severity: 'HIGH',
      regulation: 'GDPR',
      article: 'Art. 44-49',
      description: 'Cross-border data transfer requires adequate safeguards',
      remediation: 'Implement Standard Contractual Clauses (SCCs) or Binding Corporate Rules (BCRs) per Art. 46',
    });
    mitigation_measures.push('Standard Contractual Clauses', 'Data Transfer Impact Assessment');
  } else if (data_categories.length > 5 || data_subjects.length > 10000) {
    risk_level = 'MEDIUM';
    findings.push({
      finding_id: crypto.randomUUID(),
      severity: 'MEDIUM',
      regulation: 'GDPR',
      article: 'Art. 25',
      description: 'Large-scale processing requires data protection by design and default',
      remediation: 'Implement pseudonymization, data minimization, and access controls per Art. 25(1)-(2)',
    });
    mitigation_measures.push('Pseudonymization', 'Data minimization', 'Access control');
  } else {
    risk_level = 'LOW';
  }

  // DPDP Act checks
  if (data_subjects.includes('india_residents')) {
    findings.push({
      finding_id: crypto.randomUUID(),
      severity: 'MEDIUM',
      regulation: 'DPDP Act',
      article: 'Sec. 7-8',
      description: 'Data Fiduciary obligations under DPDP Act for Indian data subjects',
      remediation: 'Provide notice per Sec. 7, establish consent management framework per Sec. 5-6, appoint Data Protection Officer',
    });
    mitigation_measures.push('Consent Manager registration', 'Data Protection Officer appointment');

    if (data_categories.includes('children') || data_subjects.includes('children')) {
      findings.push({
        finding_id: crypto.randomUUID(),
        severity: 'HIGH',
        regulation: 'DPDP Act',
        article: 'Sec. 16',
        description: 'Processing children\'s personal data requires verifiable parental consent',
        remediation: 'Implement age verification and verifiable parental consent mechanisms per Sec. 16',
      });
    }
  }

  if (!cross_border_transfer) {
    mitigation_measures.push('Zero-data-egress architecture (internal network only)');
  }

  const canonical = JSON.stringify(parsed, Object.keys(parsed).sort());
  const artifact_hash = crypto.createHash('sha256').update(canonical).digest('hex');

  try {
    await axios.post(`${ORCHESTRATOR_URL}/audit/privacy`, parsed, { timeout: 10000 });
  } catch (error: any) {
    logger.warn('Privacy assessment sync failed', { run_id, error: error.message });
  }

  const phase_result = findings.some(f => f.severity === 'BLOCKER') ? 'BLOCKER' : 'PASS';

  const output = Phase4OutputSchema.parse({
    run_id,
    phase: 4,
    phase_result,
    risk_level,
    jurisdictional_conflicts,
    mitigation_measures,
    findings,
    artifact_hash,
    next_phase: 5,
  });

  return { content: [{ type: 'text', text: JSON.stringify(output, null, 2) }] };
}
