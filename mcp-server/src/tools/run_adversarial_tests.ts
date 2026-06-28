import axios from 'axios';
import { AdversarialReport } from '../types/audit.types';
import { formatExplanation } from '../utils/explainability';

const API_BASE_URL = process.env.API_BASE_URL || 'http://api:8000';

/**
 * Executes robustness suite per EU AI Act Art. 15.
 */
export async function run_adversarial_tests(input: {
  model_endpoint: string;
  test_suites: string[];
  threat_model: string;
}): Promise<AdversarialReport> {
  try {
    const response = await axios.post(`${API_BASE_URL}/audit/adversarial-tests`, input);
    const data = response.data;

    const regulatory_basis = ['EU AI Act Art. 15', 'NIST AI RMF Measure Function'];
    
    return {
      robustness_score: data.robustness_score,
      attack_surface_map: data.attack_surface_map,
      vulnerabilities: data.vulnerabilities,
      explanation: formatExplanation(data.explanation, regulatory_basis, 6),
      regulatory_basis: regulatory_basis
    };
  } catch (error) {
    throw new Error(`Failed to run adversarial tests: ${error}`);
  }
}
