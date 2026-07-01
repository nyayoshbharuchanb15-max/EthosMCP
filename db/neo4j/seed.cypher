// ============================================================================
// AI Compliance MCP Server - Neo4j Seed Data
// Sample seed data for development and testing
// ============================================================================

// ============================================================================
// 1. Create AISystem
// ============================================================================
CREATE (sys:AISystem {
    system_id: "sample-sys-1",
    system_name: "Credit Scoring Model v2",
    version: "2.1.0",
    vendor: "Internal",
    description: "Internal credit scoring model for loan eligibility assessment",
    risk_level: "HIGH",
    status: "ACTIVE",
    created_at: datetime("2025-06-01T00:00:00Z")
});

// ============================================================================
// 2. Create AuditRun
// ============================================================================
CREATE (run:AuditRun {
    run_id: "sample-run-1",
    status: "COMPLETED",
    audit_scope: "Full compliance audit per EU AI Act",
    risk_level: "HIGH",
    version: 1,
    created_at: datetime("2025-06-15T00:00:00Z"),
    completed_at: datetime("2025-06-30T00:00:00Z")
});

// ============================================================================
// 3. Link System to Run
// ============================================================================
CREATE (sys)-[:HAS_RUN {
    started_at: datetime("2025-06-15T00:00:00Z")
}]->(run);

// ============================================================================
// 4. Create Phases 1-8 with PASS status
// ============================================================================
CREATE (p1:Phase {
    run_id: "sample-run-1",
    phase_number: 1,
    phase_name: "System Registration & Inventory",
    status: "PASS",
    score: 0.95,
    started_at: datetime("2025-06-15T00:00:00Z"),
    completed_at: datetime("2025-06-16T00:00:00Z")
});
CREATE (run)-[:HAS_PHASE]->(p1);

CREATE (p2:Phase {
    run_id: "sample-run-1",
    phase_number: 2,
    phase_name: "Scope Definition & Proportionality",
    status: "PASS",
    score: 0.92,
    started_at: datetime("2025-06-16T00:00:00Z"),
    completed_at: datetime("2025-06-18T00:00:00Z")
});
CREATE (run)-[:HAS_PHASE]->(p2);

CREATE (p3:Phase {
    run_id: "sample-run-1",
    phase_number: 3,
    phase_name: "Risk Management System",
    status: "PASS",
    score: 0.88,
    started_at: datetime("2025-06-18T00:00:00Z"),
    completed_at: datetime("2025-06-21T00:00:00Z")
});
CREATE (run)-[:HAS_PHASE]->(p3);

CREATE (p4:Phase {
    run_id: "sample-run-1",
    phase_number: 4,
    phase_name: "Data Governance & Privacy",
    status: "PASS",
    score: 0.91,
    started_at: datetime("2025-06-21T00:00:00Z"),
    completed_at: datetime("2025-06-23T00:00:00Z")
});
CREATE (run)-[:HAS_PHASE]->(p4);

CREATE (p5:Phase {
    run_id: "sample-run-1",
    phase_number: 5,
    phase_name: "Bias & Fairness Assessment",
    status: "PASS",
    score: 0.85,
    started_at: datetime("2025-06-23T00:00:00Z"),
    completed_at: datetime("2025-06-25T00:00:00Z")
});
CREATE (run)-[:HAS_PHASE]->(p5);

CREATE (p6:Phase {
    run_id: "sample-run-1",
    phase_number: 6,
    phase_name: "Security & Robustness",
    status: "PASS",
    score: 0.94,
    started_at: datetime("2025-06-25T00:00:00Z"),
    completed_at: datetime("2025-06-27T00:00:00Z")
});
CREATE (run)-[:HAS_PHASE]->(p6);

CREATE (p7:Phase {
    run_id: "sample-run-1",
    phase_number: 7,
    phase_name: "Transparency & Explainability",
    status: "PASS",
    score: 0.90,
    started_at: datetime("2025-06-27T00:00:00Z"),
    completed_at: datetime("2025-06-29T00:00:00Z")
});
CREATE (run)-[:HAS_PHASE]->(p7);

CREATE (p8:Phase {
    run_id: "sample-run-1",
    phase_number: 8,
    phase_name: "Certification & Conformity",
    status: "PASS",
    score: 0.96,
    started_at: datetime("2025-06-29T00:00:00Z"),
    completed_at: datetime("2025-06-30T00:00:00Z")
});
CREATE (run)-[:HAS_PHASE]->(p8);

// ============================================================================
// 5. Create Sample Findings
// ============================================================================

// Finding: Phase 3 - Missing risk monitoring process
CREATE (f1:Finding {
    finding_id: "finding-001",
    finding_type: "RISK_MANAGEMENT",
    severity: "MEDIUM",
    title: "Continuous risk monitoring process not fully documented",
    description: "The risk management system lacks a documented process for continuous monitoring of risks post-deployment. Mitigation plan exists but is not formalized.",
    recommendation: "Implement a formal continuous risk monitoring procedure with defined review intervals and escalation paths.",
    status: "OPEN",
    created_at: datetime("2025-06-21T00:00:00Z")
});
CREATE (p3)-[:HAS_FINDING]->(f1);

// Finding: Phase 5 - Demographic parity gap
CREATE (f2:Finding {
    finding_id: "finding-002",
    finding_type: "BIAS_FAIRNESS",
    severity: "HIGH",
    title: "Demographic parity gap exceeds threshold for protected group",
    description: "Analysis shows a statistically significant difference in approval rates between demographic groups A and B (gap: 0.12, threshold: 0.08). Further investigation required.",
    recommendation: "Review training data for representation bias. Consider re-balancing or applying fairness constraints. Re-run bias assessment after mitigation.",
    status: "OPEN",
    created_at: datetime("2025-06-25T00:00:00Z")
});
CREATE (p5)-[:HAS_FINDING]->(f2);

// Finding: Phase 6 - Dependency vulnerability
CREATE (f3:Finding {
    finding_id: "finding-003",
    finding_type: "SECURITY",
    severity: "CRITICAL",
    title: "Critical vulnerability detected in third-party dependency",
    description: "Dependency scan found CVE-2025-1234 in library version 3.2.1 affecting input validation pipeline. Exploit potential is high.",
    recommendation: "Upgrade affected library to version 3.2.3 or later. Perform security regression testing after upgrade.",
    status: "CLOSED",
    resolution: "Library upgraded to 3.2.3. Security scan re-run with clean results.",
    created_at: datetime("2025-06-26T00:00:00Z"),
    resolved_at: datetime("2025-06-27T00:00:00Z")
});
CREATE (p6)-[:HAS_FINDING]->(f3);

// Finding: Phase 7 - Missing explainability for feature importance
CREATE (f4:Finding {
    finding_id: "finding-004",
    finding_type: "EXPLAINABILITY",
    severity: "LOW",
    title: "Feature importance explanations not available for all output classes",
    description: "SHAP explanations are generated only for the primary output class. Secondary class predictions lack interpretability.",
    recommendation: "Extend explanation generation to cover all output classes. Update model card with explanation coverage details.",
    status: "OPEN",
    created_at: datetime("2025-06-29T00:00:00Z")
});
CREATE (p7)-[:HAS_FINDING]->(f4);

// ============================================================================
// 6. Create Certificate
// ============================================================================
CREATE (cert:Certificate {
    cert_id: "cert-001",
    run_id: "sample-run-1",
    system_id: "sample-sys-1",
    certificate_type: "EU_AI_ACT_CONFORMITY",
    status: "ISSUED",
    valid_from: datetime("2025-07-01T00:00:00Z"),
    valid_until: datetime("2026-06-30T00:00:00Z"),
    issued_at: datetime("2025-07-01T00:00:00Z")
});
CREATE (run)-[:PRODUCED]->(cert);
CREATE (sys)-[:HAS_CERTIFICATE]->(cert);

// ============================================================================
// 7. Create ROPA Record
// ============================================================================
CREATE (ropa:ROPA {
    system_id: "sample-sys-1",
    system_name: "Credit Scoring Model v2",
    data_controller: "ACME Financial Services Ltd",
    data_processor: "Internal AI Platform Team",
    processing_purpose: "Automated creditworthiness assessment for loan applications",
    data_categories: ["Personal identifiers", "Financial history", "Employment data", "Credit history"],
    data_subject_categories: ["Loan applicants", "Joint applicants"],
    retention_period: "36 months post-application",
    legal_basis: "GDPR Art. 6(1)(f) - Legitimate interests",
    cross_border_transfer: false,
    safeguards: "Data pseudonymized at rest. Access control via RBAC. Audit logging enabled.",
    version: 1,
    created_at: datetime("2025-06-01T00:00:00Z")
});
CREATE (sys)-[:HAS_ROPA]->(ropa);

// ============================================================================
// 8. Create Consent Record
// ============================================================================
CREATE (subject:DataSubject {
    subject_id: "ds-001",
    email: "user@example.com"
});
CREATE (consent:ConsentRecord {
    consent_id: "consent-001",
    data_subject_id: "ds-001",
    system_id: "sample-sys-1",
    consent_type: "DATA_PROCESSING",
    status: "GRANTED",
    granted_at: datetime("2025-06-01T00:00:00Z"),
    expires_at: datetime("2026-06-01T00:00:00Z")
});
CREATE (subject)-[:GAVE]->(consent);
CREATE (sys)-[:HAS_CONSENT]->(consent);

// ============================================================================
// 9. Create DSAR Request
// ============================================================================
CREATE (dsar:DSARRequest {
    request_id: "dsar-001",
    data_subject_id: "ds-001",
    request_type: "ACCESS",
    status: "FULFILLED",
    details: {
        scope: "All personal data processed by Credit Scoring Model",
        preferred_format: "JSON"
    },
    fulfilled_at: datetime("2025-06-10T00:00:00Z"),
    deadline: datetime("2025-07-01T00:00:00Z"),
    created_at: datetime("2025-06-05T00:00:00Z")
});
CREATE (subject)-[:MADE]->(dsar);
CREATE (sys)-[:RECEIVED]->(dsar);

// ============================================================================
// 10. Create Erasure Request
// ============================================================================
CREATE (erasure:ErasureRequest {
    request_id: "erasure-001",
    data_subject_id: "ds-001",
    system_id: "sample-sys-1",
    scope: {
        tables: ["user_profile", "application_history"],
        cascading: true
    },
    status: "COMPLETED",
    executed_at: datetime("2025-06-12T00:00:00Z"),
    verified_at: datetime("2025-06-13T00:00:00Z"),
    created_at: datetime("2025-06-11T00:00:00Z")
});
CREATE (subject)-[:REQUESTED_ERASURE]->(erasure);
CREATE (sys)-[:RECEIVED]->(erasure);

// ============================================================================
// Return summary counts
// ============================================================================
RETURN
    COUNT(DISTINCT sys) AS AISystems,
    COUNT(DISTINCT run) AS AuditRuns,
    COUNT(DISTINCT p1) + COUNT(DISTINCT p2) + COUNT(DISTINCT p3) +
    COUNT(DISTINCT p4) + COUNT(DISTINCT p5) + COUNT(DISTINCT p6) +
    COUNT(DISTINCT p7) + COUNT(DISTINCT p8) AS Phases,
    COUNT(DISTINCT f1) + COUNT(DISTINCT f2) + COUNT(DISTINCT f3) +
    COUNT(DISTINCT f4) AS Findings;
