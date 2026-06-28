import axios from 'axios';
import { AuditCertificate } from '../types/certificate.types';
import { formatExplanation } from '../utils/explainability';

const API_BASE_URL = process.env.API_BASE_URL || 'http://api:8000';

/**
 * Issues signed W3C VC 2.0 audit certificate per EU AI Act Art. 26.
 */
export async function generate_audit_certificate(input: {
  audit_session_id: string;
  weighted_audit_score: any;
  blocker_fail_detected: boolean;
}): Promise<AuditCertificate> {
  try {
    const response = await axios.post(`${API_BASE_URL}/audit/generate-certificate`, input);
    const data = response.data;

    const regulatory_basis = ['EU AI Act Art. 26', 'NIST AI RMF Govern Function'];
    
    return {
      vc_json: data.vc_json,
      pdf_base64: data.pdf_base64,
      issued_at: data.issued_at,
      explanation: formatExplanation(data.explanation, regulatory_basis, 8),
      regulatory_basis: regulatory_basis
    };
  } catch (error) {
    throw new Error(`Failed to generate audit certificate: ${error}`);
  }
}
