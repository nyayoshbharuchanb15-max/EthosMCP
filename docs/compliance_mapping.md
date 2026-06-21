# EthosMCP Compliance Mapping

This document provides a detailed mapping of key statutory provisions from the EU AI Act, GDPR, and India\'s DPDP Act to the audit vectors and checks implemented within the EthosMCP framework.

## 1. GDPR (General Data Protection Regulation - EU)

| Statutory Provision | EthosMCP Audit Vector | Description |
| :------------------ | :-------------------- | :---------- |
| **Art. 30 (ROPA)** | Phase 1: Governance validation (`governance.py`) | Verifies the existence and accuracy of Records of Processing Activities, ensuring all data processing has a legal basis and defined purpose. |
| **Arts. 15-17 (DSAR/Erasure)** | Phase 3: Erasure latency simulation (`sovereignty.py`) | Simulates Data Subject Access Requests and erasure requests to ensure timely and complete fulfillment across all data layers. |
| **Art. 33 (Breach Notification)** | Phase 4: Breach automation (`security.py`) | Checks for automated breach detection and notification workflows, ensuring compliance with reporting timelines. |
| **Art. 25 (Privacy by Design)** | Architectural Principle | Ensured by the overall system design, which prioritizes data minimization, pseudonymization, and security from the outset. |

## 2. DPDP Act (Digital Personal Data Protection Act - India)

| Statutory Provision | EthosMCP Audit Vector | Description |
| :------------------ | :-------------------- | :---------- |
| **Sec. 5 (Notice)** | Phase 3: Multi-lingual notice audit (`sovereignty.py`) | Verifies that data principals receive clear, concise, and multi-lingual notices regarding data processing activities. |
| **Sec. 6 (Consent)** | Phase 3: Granular consent state logging (`sovereignty.py`) | Audits the granularity and validity of consent mechanisms, ensuring consent is freely given, specific, informed, and unambiguous. |
| **Sec. 10 (Erasure)** | Phase 3: Erasure propagation (`sovereignty.py`) | Checks that data erasure requests propagate effectively across all primary stores, backups, and third-party processors. |
| **Sec. 11-14 (Data Principal Rights)** | Phase 3: Rights fulfillment pipeline (`sovereignty.py`) | Evaluates the system\'s ability to operationalize and fulfill various data principal rights, including access, correction, and grievance redressal. |

## 3. EU AI Act (Artificial Intelligence Act - EU)

| Statutory Provision | EthosMCP Audit Vector | Description |
| :------------------ | :-------------------- | :---------- |
| **Art. 10 (High-risk training data)** | Phase 1: Training dataset lineage (`governance.py`) | Verifies the documentation and governance of training datasets used for high-risk AI systems, including data quality and bias mitigation. |
| **Chapter III (Technical documentation)** | Phase 2: Model bias logging (`localization.py`) | Ensures that comprehensive technical documentation for AI systems is maintained, including information on data, training, and performance. |
| **ISO/IEC 42001 (Risk governance)** | Phase 4: Operational risk governance alignment (`security.py`) | Assesses the alignment of AI system risk management processes with international standards for AI management systems. |
