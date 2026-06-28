import axios from 'axios';
import { ProvenanceReport } from '../types/audit.types';
import { formatExplanation } from '../utils/explainability';

const API_BASE_URL = process.env.API_BASE_URL || 'http://api:8000';

/**
 * Scans model provenance and data lineage per GDPR Art. 5 and ISO 42001.
 */
export async function audit_supply_chain(input: {
  model_id: string;
  data_sources: string[];
  third_party_components: string[];
}): Promise<ProvenanceReport> {
  try {
    const response = await axios.post(`${API_BASE_URL}/audit/supply-chain`, input);
    const data = response.data;

    const regulatory_basis = ['GDPR Art. 5', 'ISO 42001 Clause 6'];
    
    return {
      ip_risk_score: data.ip_risk_score,
      lineage_complete: data.lineage_complete,
      findings: data.findings,
      explanation: formatExplanation(data.explanation, regulatory_basis, 2),
      regulatory_basis: regulatory_basis
    };
  } catch (error) {
    throw new Error(`Failed to audit supply chain: ${error}`);
  }
}
