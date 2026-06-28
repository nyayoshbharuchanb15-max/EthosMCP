import axios from 'axios';
import { DPIAReport } from '../types/audit.types';
import { formatExplanation } from '../utils/explainability';

const API_BASE_URL = process.env.API_BASE_URL || 'http://api:8000';

/**
 * Generates GDPR Art. 35 DPIA and checks cross-border transfer mechanisms.
 */
export async function generate_dpia(input: {
  processing_activity: string;
  data_categories: string[];
  data_subjects: string[];
  recipients: string[];
  storage_location: string;
  transfer_mechanisms: string[];
}): Promise<DPIAReport> {
  try {
    const response = await axios.post(`${API_BASE_URL}/audit/dpia`, input);
    const data = response.data;

    const regulatory_basis = ['GDPR Art. 35', 'GDPR Art. 35(7)(d)', 'GDPR Art. 44-49', 'ISO 42001 Clause 7'];
    
    return {
      risk_level: data.risk_level,
      jurisdictional_conflicts: data.jurisdictional_conflicts,
      mitigation_measures: data.mitigation_measures,
      explanation: formatExplanation(data.explanation, regulatory_basis, 5),
      regulatory_basis: regulatory_basis
    };
  } catch (error) {
    throw new Error(`Failed to generate DPIA: ${error}`);
  }
}
