export interface RegulatoryCitation {
  article: string;
  name: string;
  summary: string;
  framework: 'EU AI Act' | 'GDPR' | 'NIST AI RMF' | 'ISO 42001';
}

export interface ExplainableResult {
  explanation: string;
  regulatory_basis: string[];
}
