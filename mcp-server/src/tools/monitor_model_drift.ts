import axios from 'axios';
import { DriftAlert } from '../types/certificate.types';
import { formatExplanation } from '../utils/explainability';

const API_BASE_URL = process.env.API_BASE_URL || 'http://api:8000';

/**
 * Continuous post-deployment monitoring per EU AI Act Art. 35.
 */
export async function monitor_model_drift(input: {
  model_id: string;
  production_data_stream: string;
  baseline_data_ref: string;
  monitoring_thresholds: Record<string, number>;
}): Promise<DriftAlert> {
  try {
    const response = await axios.post(`${API_BASE_URL}/audit/monitor-drift`, input);
    const data = response.data;

    const regulatory_basis = ['EU AI Act Art. 35', 'ISO 42001 Clause 8'];
    
    return {
      drift_detected: data.drift_detected,
      drift_metrics: data.drift_metrics,
      threshold_exceeded: data.threshold_exceeded,
      reaudit_recommended: data.reaudit_recommended,
      explanation: formatExplanation(data.explanation, regulatory_basis, 9),
      regulatory_basis: regulatory_basis
    };
  } catch (error) {
    throw new Error(`Failed to monitor model drift: ${error}`);
  }
}
