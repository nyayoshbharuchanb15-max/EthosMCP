# AI Governance MCP Server: Regulatory Mapping

This document provides a comprehensive cross-reference between key regulatory provisions and the specific components and phases within the AI Governance MCP Server that address them. This mapping ensures transparency and demonstrates how the architectural design operationalizes legal and ethical requirements.

| Provision | Full Name | Framework | Phase | Tool/Service | Output Field |
|---|---|---|---|---|---|
| EU AI Act Art. 9 | Risk Management System | EU AI Act | 1 | `classify_ai_risk` | `RiskTierResult` |
| EU AI Act Art. 10(2)(f) | Data Governance and Quality (Bias) | EU AI Act | 4 | `run_bias_assessment` | `BiasReport` |
| EU AI Act Art. 13 | Human Oversight | EU AI Act | 3 | `verify_human_oversight` | `OversightCertificate` |
| EU AI Act Art. 14 | Human Oversight (Technical Measures) | EU AI Act | 3 | `verify_human_oversight` | `OversightCertificate` |
| EU AI Act Art. 15 | Robustness and Accuracy | EU AI Act | 6 | `run_adversarial_tests` | `AdversarialReport` |
| EU AI Act Art. 26 | Conformity Assessment | EU AI Act | 8 | `generate_audit_certificate` | `AuditCertificate` |
| EU AI Act Art. 35 | Post-market Monitoring | EU AI Act | 9 | `monitor_model_drift` | `DriftAlert` |
| GDPR Art. 5 | Principles relating to processing of personal data | GDPR | 2 | `audit_supply_chain` | `ProvenanceReport` |
| GDPR Art. 25 | Data protection by design and by default | GDPR | 5 | `generate_dpia` | `DPIAReport` |
| GDPR Art. 35 | Data protection impact assessment | GDPR | 5 | `generate_dpia` | `DPIAReport` |
| GDPR Art. 44-49 | Transfers of personal data to third countries or international organisations | GDPR | 5 | `generate_dpia` | `DPIAReport` |
| NIST AI RMF Govern | Govern Function | NIST AI RMF | 1, 3, 5, 8 | `classify_ai_risk`, `verify_human_oversight`, `generate_dpia`, `generate_audit_certificate` | `RiskTierResult`, `OversightCertificate`, `DPIAReport`, `AuditCertificate` |
| NIST AI RMF Map | Map Function | NIST AI RMF | 2, 4 | `audit_supply_chain`, `run_bias_assessment` | `ProvenanceReport`, `BiasReport` |
| NIST AI RMF Measure | Measure Function | NIST AI RMF | 6, 7, 9 | `run_adversarial_tests`, `score_audit_weighted`, `monitor_model_drift` | `AdversarialReport`, `WeightedAuditScore`, `DriftAlert` |
| NIST AI RMF Manage | Manage Function | NIST AI RMF | 9 | `monitor_model_drift` | `DriftAlert` |
| ISO 42001 Clause 6 | AI system planning and control | ISO 42001 | 1, 2 | `classify_ai_risk`, `audit_supply_chain` | `RiskTierResult`, `ProvenanceReport` |
| ISO 42001 Clause 7 | AI system impact assessment | ISO 42001 | 5 | `generate_dpia` | `DPIAReport` |
| ISO 42001 Clause 8 | AI system operation | ISO 42001 | 3, 9 | `verify_human_oversight`, `monitor_model_drift` | `OversightCertificate`, `DriftAlert` |
