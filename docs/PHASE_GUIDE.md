Non-Compliant").
    *   `explanation`: `string` - Plain-language explanation of the overall score and its implications.
    *   `regulatory_basis`: `string[]` - Array of regulatory articles.
    *   `blocking`: `boolean` - True if the score results in a `BLOCKER_FAIL`.
*   **Blocker Conditions:** If the `overall_score` falls below a predefined critical threshold, a `BLOCKER_FAIL` is emitted, halting the audit pipeline and preventing certificate issuance.
*   **Example Output (Pass):**
    ```json
    {
      "overall_score": 92.5,
      "score_breakdown": {
        "risk_classification": 100,
        "supply_chain": 95,
        "human_oversight": 100,
        "bias_assessment": 85,
        "dpia_generation": 90,
        "adversarial_testing": 90
      },
      "compliance_status": "Compliant",
      "explanation": "The AI system has achieved an overall risk-weighted audit score of 92.5%, indicating strong compliance across all regulatory domains. Minor areas for improvement were noted in bias mitigation, but do not prevent certification.",
      "regulatory_basis": ["NIST AI RMF Measure Function"],
      "blocking": false
    }
    ```
*   **Example Output (Fail):**
    ```json
    {
      "overall_score": 45.0,
      "score_breakdown": {
        "risk_classification": 100,
        "supply_chain": 70,
        "human_oversight": 0,
        "bias_assessment": 50,
        "dpia_generation": 60,
        "adversarial_testing": 75
      },
      "compliance_status": "Non-Compliant",
      "explanation": "BLOCKER_FAIL: The AI system's overall risk-weighted audit score of 45.0% is below the critical threshold for certification. This is primarily due to a BLOCKER_FAIL in human oversight verification (Phase 3) and significant issues in bias assessment. Certification cannot be issued.",
      "regulatory_basis": ["NIST AI RMF Measure Function"],
      "blocking": true
    }
    ```
*   **Regulatory Provisions Satisfied:** NIST AI RMF Measure Function.

---

## Phase 8: Audit Certificate Generation

*   **Phase Name:** Audit Certificate Generation
*   **Tool Name:** `generate_audit_certificate`
*   **What it tests and why it matters legally:** This phase issues a signed audit certificate or a structured fail notice. The certificate conforms to W3C Verifiable Credentials 2.0, making it machine-readable and cryptographically verifiable. Legally, this provides formal proof of compliance (or non-compliance) with regulatory requirements, essential for accountability, regulatory submissions, and building trust. It satisfies EU AI Act Art. 26 on conformity assessment.
*   **Input Parameters:**
    *   `audit_session_id`: `string` - Identifier for the current audit session.
    *   `weighted_audit_score`: `object` - The `WeightedAuditScore` object from Phase 7.
    *   `blocker_fail_detected`: `boolean` - True if any `BLOCKER_FAIL` was detected in previous phases.
*   **Output Schema:** `AuditCertificate` | `FailNotice`
    *   `vc_json`: `object` - The W3C Verifiable Credential in JSON format.
    *   `pdf_base64`: `string` - Base64 encoded PDF representation of the certificate.
    *   `issued_at`: `string` - ISO 8601 timestamp of issuance.
    *   `explanation`: `string` - Plain-language explanation of the certificate or fail notice.
    *   `regulatory_basis`: `string[]` - Array of regulatory articles.
*   **Blocker Conditions:** Never issues a certificate if any `BLOCKER_FAIL` exists in the Evidence Store for this audit session.
*   **Example Output (Certificate):**
    ```json
    {
      "vc_json": {
        "@context": ["https://www.w3.org/ns/credentials/v2"],
        "type": ["VerifiableCredential", "AIAuditCertificate"],
        "issuer": "did:key:z6MkhaXgBZDzqzthE2t5JLafwGSGPj3NjJqxYW1D6J9d6d",
        "issuanceDate": "2026-06-28T10:30:00Z",
        "credentialSubject": {
          "id": "did:example:123",
          "auditSessionId": "audit-session-abc-123",
          "overallScore": 92.5,
          "complianceStatus": "Compliant",
          "scoreBreakdown": {
            "risk_classification": 100,
            "supply_chain": 95,
            "human_oversight": 100,
            "bias_assessment": 85,
            "dpia_generation": 90,
            "adversarial_testing": 90
          }
        },
        "proof": {
          "type": "Ed25519Signature2020",
          "created": "2026-06-28T10:30:00Z",
          "verificationMethod": "did:key:z6MkhaXgBZDzqzthE2t5JLafwGSGPj3NjJqxYW1D6J9d6d#z6MkhaXgBZDzqzthE2t5JLafwGSGPj3NjJqxYW1D6J9d6d",
          "proofPurpose": "assertionMethod",
          "jws": "eyJhbGciOiJFZERTQSIsImI2NCI6ZmFsc2UsImNyaXQiOlsiYjY0Il19..some_signature_string"
        }
      },
      "pdf_base64": "JVBERi0xLjQ...",
      "issued_at": "2026-06-28T10:30:00Z",
      "explanation": "A W3C Verifiable Credential has been successfully issued, certifying the AI system's compliance with regulatory requirements based on an overall audit score of 92.5%. This fulfills the conformity assessment obligations under EU AI Act Article 26.",
      "regulatory_basis": ["EU AI Act Art. 26", "NIST AI RMF Govern Function"]
    }
    ```
*   **Example Output (Fail Notice):**
    ```json
    {
      "fail_notice_id": "fail-notice-xyz-456",
      "audit_session_id": "audit-session-abc-123",
      "reason": "BLOCKER_FAIL detected in Human Oversight Verification (Phase 3).",
      "details": "The AI system failed to demonstrate the existence of a functional kill-switch, a critical requirement under EU AI Act Article 14(4).",
      "issued_at": "2026-06-28T10:30:00Z",
      "explanation": "A Fail Notice has been issued due to a BLOCKER_FAIL in Phase 3 (Human Oversight Verification). The system does not meet the minimum safety requirements for certification under the EU AI Act.",
      "regulatory_basis": ["EU AI Act Art. 14(4)"]
    }
    ```
*   **Regulatory Provisions Satisfied:** EU AI Act Art. 26 (Conformity Assessment), NIST AI RMF Govern Function.

---

## Phase 9: Model Drift Monitoring

*   **Phase Name:** Model Drift Monitoring
*   **Tool Name:** `monitor_model_drift`
*   **What it tests and why it matters legally:** This phase provides continuous post-deployment monitoring for model drift using tools like Evidently AI. Legally, this addresses the EU AI Act Art. 35 requirement for post-market monitoring. It ensures that the AI system's performance, fairness, and robustness do not degrade over time due to changes in data distributions or real-world conditions, which could lead to new risks or non-compliance.
*   **Input Parameters:**
    *   `model_id`: `string` - Identifier for the AI model.
    *   `production_data_stream`: `string` - Reference to the live production data stream.
    *   `baseline_data_ref`: `string` - Reference to the baseline data used for training.
    *   `monitoring_thresholds`: `object` - Configuration for drift detection thresholds.
*   **Output Schema:** `DriftAlert` | `ReauditTrigger`
    *   `drift_detected`: `boolean` - True if model drift is detected.
    *   `drift_metrics`: `object` - Metrics indicating the nature and severity of drift.
    *   `threshold_exceeded`: `string[]` - List of thresholds that were exceeded.
    *   `reaudit_recommended`: `boolean` - True if a reaudit is recommended due to severe drift.
    *   `explanation`: `string` - Plain-language explanation of drift findings.
    *   `regulatory_basis`: `string[]` - Array of regulatory articles.
*   **Blocker Conditions:** None.
*   **Example Output (Drift Detected):**
    ```json
    {
      "drift_detected": true,
      "drift_metrics": {
        "data_drift_score": 0.75,
        "concept_drift_score": 0.60,
        "feature_drift": {"age": 0.3, "income": 0.2}
      },
      "threshold_exceeded": ["data_drift_score", "concept_drift_score"],
      "reaudit_recommended": true,
      "explanation": "Significant model drift detected in production data compared to baseline, exceeding predefined thresholds for both data and concept drift. This indicates a potential degradation in model performance and fairness, necessitating a reaudit as per EU AI Act Article 35.",
      "regulatory_basis": ["EU AI Act Art. 35", "NIST AI RMF Measure Function", "NIST AI RMF Manage Function", "ISO 42001 Clause 8"]
    }
    ```
*   **Regulatory Provisions Satisfied:** EU AI Act Art. 35 (Post-market Monitoring), NIST AI RMF Measure Function, NIST AI RMF Manage Function, ISO 42001 Clause 8 (AI system operation).
