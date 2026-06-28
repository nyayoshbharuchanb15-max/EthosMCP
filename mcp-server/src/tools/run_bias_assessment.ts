import axios from 'axios';
import { BiasReport } from '../types/audit.types';
import { formatExplanation } from '../utils/explainability';

const API_BASE_URL = process.env.API_BASE_URL || 'http://api:8000';

/**
 * Interface to the Python bias engine per EU AI Act Art. 10(2)(f).
 */
export async function run_bias_assessment(input: {
  model_endpoint: string;
  test_dataset_ref: string;
  protected_classes: string[];
  intersectional: boolean;
}): Promise<BiasReport> {
  try {
    const response = await axios.post(`${API_BASE_URL}/audit/bias-assessment`, input);
    const data = response.data;

    const regulatory_basis = ['EU AI Act Art. 10(2)(f)', 'NIST AI RMF Map Function'];
    
    return {
      disparity_scores: data.disparity_scores,
      findings: data.findings,
      worst_performing_group: data.worst_performing_group,
      explanation: formatExplanation(data.explanation, regulatory_basis, 4),
      regulatory_basis: regulatory_basis
    };
  } catch (error) {
    throw new Error(`Failed to run bias assessment: ${error}`);
  }
}
