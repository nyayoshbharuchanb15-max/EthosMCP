import { RegulatoryCitation } from '../types/regulatory.types';

export const REGULATORY_CITATIONS: Record<string, RegulatoryCitation> = {
  'EU AI Act Art. 9': {
    article: 'Art. 9',
    name: 'Risk Management System',
    summary: 'Establishes requirements for a continuous iterative process throughout the entire lifecycle of a high-risk AI system.',
    framework: 'EU AI Act'
  },
  'EU AI Act Art. 10(2)(f)': {
    article: 'Art. 10(2)(f)',
    name: 'Data Governance and Quality (Bias)',
    summary: 'Requires examination of possible biases in data sets used for training, validation, and testing.',
    framework: 'EU AI Act'
  },
  'EU AI Act Art. 13': {
    article: 'Art. 13',
    name: 'Transparency and Provision of Information',
    summary: 'Requires high-risk AI systems to be designed and developed in such a way as to ensure that their operation is sufficiently transparent.',
    framework: 'EU AI Act'
  },
  'EU AI Act Art. 14': {
    article: 'Art. 14',
    name: 'Human Oversight',
    summary: 'High-risk AI systems shall be designed and developed in such a way that they can be effectively overseen by natural persons.',
    framework: 'EU AI Act'
  },
  'EU AI Act Art. 14(4)': {
    article: 'Art. 14(4)',
    name: 'Human Oversight (Kill-switch)',
    summary: 'Requires the ability for human operators to effectively oversee the AI system, including the ability to intervene or shut it down.',
    framework: 'EU AI Act'
  },
  'EU AI Act Art. 15': {
    article: 'Art. 15',
    name: 'Accuracy, Robustness and Cybersecurity',
    summary: 'High-risk AI systems shall be designed and developed to achieve an appropriate level of accuracy, robustness, and cybersecurity.',
    framework: 'EU AI Act'
  },
  'EU AI Act Art. 26': {
    article: 'Art. 26',
    name: 'Conformity Assessment',
    summary: 'Requires high-risk AI systems to undergo a conformity assessment procedure prior to being placed on the market.',
    framework: 'EU AI Act'
  },
  'EU AI Act Art. 35': {
    article: 'Art. 35',
    name: 'Post-market Monitoring',
    summary: 'Requires providers to establish and document a post-market monitoring system to collect and analyze data on the performance of high-risk AI systems.',
    framework: 'EU AI Act'
  },
  'GDPR Art. 5': {
    article: 'Art. 5',
    name: 'Principles relating to processing of personal data',
    summary: 'Defines the core principles of data protection, including lawfulness, fairness, transparency, and purpose limitation.',
    framework: 'GDPR'
  },
  'GDPR Art. 25': {
    article: 'Art. 25',
    name: 'Data protection by design and by default',
    summary: 'Requires technical and organizational measures to implement data protection principles effectively.',
    framework: 'GDPR'
  },
  'GDPR Art. 35': {
    article: 'Art. 35',
    name: 'Data protection impact assessment',
    summary: 'Mandates an assessment of the impact of envisaged processing operations on the protection of personal data.',
    framework: 'GDPR'
  },
  'GDPR Art. 35(7)(d)': {
    article: 'Art. 35(7)(d)',
    name: 'DPIA - Measures to address risks',
    summary: 'Requires the DPIA to include measures envisaged to address the risks, including safeguards and security measures.',
    framework: 'GDPR'
  },
  'NIST AI RMF Govern': {
    article: 'Govern',
    name: 'Govern Function',
    summary: 'Cultivates a culture of risk management and provides the foundation for the other functions.',
    framework: 'NIST AI RMF'
  },
  'NIST AI RMF Map': {
    article: 'Map',
    name: 'Map Function',
    summary: 'Establishes the context to identify risks and potential benefits of an AI system.',
    framework: 'NIST AI RMF'
  },
  'NIST AI RMF Measure': {
    article: 'Measure',
    name: 'Measure Function',
    summary: 'Employs quantitative, semi-quantitative, or qualitative tools to analyze and monitor AI risk.',
    framework: 'NIST AI RMF'
  },
  'NIST AI RMF Manage': {
    article: 'Manage',
    name: 'Manage Function',
    summary: 'Allocates risk management resources to mapped and measured risks on a regular basis.',
    framework: 'NIST AI RMF'
  },
  'ISO 42001 Clause 6': {
    article: 'Clause 6',
    name: 'AI system planning and control',
    summary: 'Specifies requirements for planning and controlling AI system development and deployment.',
    framework: 'ISO 42001'
  },
  'ISO 42001 Clause 7': {
    article: 'Clause 7',
    name: 'AI system impact assessment',
    summary: 'Requires assessing the impacts of AI systems on individuals and society.',
    framework: 'ISO 42001'
  },
  'ISO 42001 Clause 8': {
    article: 'Clause 8',
    name: 'AI system operation',
    summary: 'Focuses on the operational aspects of AI systems, including monitoring and maintenance.',
    framework: 'ISO 42001'
  }
};

export function getRegulatorySummary(citation: string): string {
  return REGULATORY_CITATIONS[citation]?.summary || 'Regulatory requirement for AI governance.';
}
