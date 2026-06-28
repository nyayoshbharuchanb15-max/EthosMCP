import axios from 'axios';
import { OversightCertificate, FailNotice } from '../types/audit.types';
import { formatExplanation } from '../utils/explainability';

const API_BASE_URL = process.env.API_BASE_URL || 'http://api:8000';

/**
 * Verifies kill-switch accessibility per EU AI Act Art. 14(4).
 * "High-risk AI systems shall be designed and developed in such a way that they can be effectively overseen by natural persons..."
 */
export async function verify_human_oversight(input: {
  architecture_description: string;
  has_kill_switch: boolean;
  override_mechanism: boolean;
  monitoring_capability: boolean;
  automation_bias_mitigations: boolean;
}): Promise<OversightCertificate | FailNotice> {
  try {
    const response = await axios.post(`${API_BASE_URL}/audit/human-oversight`, input);
    const data = response.data;

    const regulatory_basis = ['EU AI Act Art. 14', 'EU AI Act Art. 14(4)'];
    
    if (data.result === 'BLOCKER_FAIL') {
      return {
        fail_notice_id: `FAIL-${Date.now()}`,
        audit_session_id: data.audit_session_id,
        reason: 'BLOCKER_FAIL',
        details: data.explanation,
        issued_at: new Date().toISOString(),
        explanation: formatExplanation(data.explanation, regulatory_basis, 3),
        regulatory_basis: regulatory_basis
      } as FailNotice;
    }

    return {
      has_kill_switch: data.has_kill_switch,
      override_capability: data.override_capability,
      compliance_status: data.compliance_status,
      explanation: formatExplanation(data.explanation, regulatory_basis, 3),
      regulatory_basis: regulatory_basis
    };
  } catch (error) {
    throw new Error(`Failed to verify human oversight: ${error}`);
  }
}
