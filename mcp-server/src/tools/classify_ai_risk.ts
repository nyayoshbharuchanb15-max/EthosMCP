import axios from 'axios';
import { RiskTierResult } from '../types/risk.types';
import { formatExplanation } from '../utils/explainability';

const API_BASE_URL = process.env.API_BASE_URL || 'http://api:8000';

/**
 * Classifies AI system into EU AI Act risk tier per Art. 9.
 * Handles PROHIBITED, HIGH, LIMITED, and MINIMAL tiers.
 */
export async function classify_ai_risk(input: {
  system_name: string;
  use_case: string;
  deployment_context: string;
  processes_biometric_data: boolean;
  used_in_critical_infra: boolean;
  affects_access_to_services: boolean;
  autonomous_decision: boolean;
}): Promise<RiskTierResult> {
  try {
    const response = await axios.post(`${API_BASE_URL}/audit/classify-risk`, input);
    const data = response.data;

    const regulatory_basis = ['EU AI Act Art. 9'];
    if (data.tier === 'HIGH') regulatory_basis.push('EU AI Act Annex III');
    
    return {
      tier: data.tier,
      blocking: data.blocking,
      annex_iii_domain: data.annex_iii_domain,
      explanation: formatExplanation(data.explanation, regulatory_basis, 1),
      regulatory_basis: regulatory_basis
    };
  } catch (error) {
    throw new Error(`Failed to classify AI risk: ${error}`);
  }
}
