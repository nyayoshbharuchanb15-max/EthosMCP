import axios from 'axios';
import { WeightedAuditScore } from '../types/audit.types';
import { formatExplanation } from '../utils/explainability';

const API_BASE_URL = process.env.API_BASE_URL || 'http://api:8000';

/**
 * Risk-weighted scoring engine per NIST AI RMF.
 */
export async function score_audit_weighted(input: {
  audit_session_id: string;
  phase_results: any[];
}): Promise<WeightedAuditScore> {
  try {
    const response = await axios.post(`${API_BASE_URL}/audit/weighted-score`, input);
    const data = response.data;

    const regulatory_basis = ['NIST AI RMF Measure Function'];
    
    return {
      overall_score: data.overall_score,
      score_breakdown: data.score_breakdown,
      compliance_status: data.compliance_status,
      blocking: data.blocking,
      explanation: formatExplanation(data.explanation, regulatory_basis, 7),
      regulatory_basis: regulatory_basis
    };
  } catch (error) {
    throw new Error(`Failed to score audit: ${error}`);
  }
}
