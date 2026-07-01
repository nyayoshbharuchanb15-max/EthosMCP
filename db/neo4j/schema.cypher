// ============================================================================
// AI Compliance MCP Server - Neo4j Schema
// Constraints, indexes, and graph model
// ============================================================================

// ============================================================================
// CONSTRAINTS (ensure uniqueness)
// ============================================================================

CREATE CONSTRAINT unique_aisystem_system_id IF NOT EXISTS
FOR (s:AISystem) REQUIRE s.system_id IS UNIQUE;

CREATE CONSTRAINT unique_auditrun_run_id IF NOT EXISTS
FOR (r:AuditRun) REQUIRE r.run_id IS UNIQUE;

CREATE CONSTRAINT unique_phase_run_phase IF NOT EXISTS
FOR (p:Phase) REQUIRE (p.run_id, p.phase_number) IS UNIQUE;

CREATE CONSTRAINT unique_finding_finding_id IF NOT EXISTS
FOR (f:Finding) REQUIRE f.finding_id IS UNIQUE;

CREATE CONSTRAINT unique_certificate_cert_id IF NOT EXISTS
FOR (c:Certificate) REQUIRE c.cert_id IS UNIQUE;

CREATE CONSTRAINT unique_ropa_system_id IF NOT EXISTS
FOR (r:ROPA) REQUIRE r.system_id IS UNIQUE;

CREATE CONSTRAINT unique_dsar_request_id IF NOT EXISTS
FOR (d:DSARRequest) REQUIRE d.request_id IS UNIQUE;

CREATE CONSTRAINT unique_erasure_request_id IF NOT EXISTS
FOR (e:ErasureRequest) REQUIRE e.request_id IS UNIQUE;

// ============================================================================
// INDEXES (performance)
// ============================================================================

CREATE INDEX idx_aisystem_system_name IF NOT EXISTS
FOR (s:AISystem) ON (s.system_name);

CREATE INDEX idx_auditrun_status IF NOT EXISTS
FOR (r:AuditRun) ON (r.status);

CREATE INDEX idx_finding_severity IF NOT EXISTS
FOR (f:Finding) ON (f.severity);

CREATE INDEX idx_phase_status IF NOT EXISTS
FOR (p:Phase) ON (p.status);

CREATE INDEX idx_auditrun_created_at IF NOT EXISTS
FOR (r:AuditRun) ON (r.created_at);

CREATE INDEX idx_finding_type IF NOT EXISTS
FOR (f:Finding) ON (f.finding_type);

CREATE INDEX idx_certificate_status IF NOT EXISTS
FOR (c:Certificate) ON (c.status);

CREATE INDEX idx_certificate_system_id IF NOT EXISTS
FOR (c:Certificate) ON (c.system_id);

CREATE INDEX idx_phase_phase_number IF NOT EXISTS
FOR (p:Phase) ON (p.phase_number);

CREATE INDEX idx_dsar_status IF NOT EXISTS
FOR (d:DSARRequest) ON (d.status);

// ============================================================================
// FULL-TEXT INDEXES (for search)
// ============================================================================

CREATE FULLTEXT INDEX ft_aisystem_name_description IF NOT EXISTS
FOR (s:AISystem) ON EACH [s.system_name, s.description];

CREATE FULLTEXT INDEX ft_finding_title_description IF NOT EXISTS
FOR (f:Finding) ON EACH [f.title, f.description];

// ============================================================================
// NODE LABELS AND RELATIONSHIP TYPES REFERENCE
// ============================================================================
//
// Node Labels:
//   AISystem      - An AI system under audit
//   AuditRun      - An audit execution run
//   Phase         - A phase within an audit run (1-8)
//   Finding       - A finding discovered during an audit
//   Certificate   - A compliance certificate issued
//   ROPA          - Record of Processing Activities
//   DSARRequest   - Data Subject Access Request
//   ErasureRequest - Right to Erasure request
//   ConsentRecord - Consent tracking record
//
// Relationship Types:
//   (:AISystem)-[:HAS_RUN]->(:AuditRun)
//   (:AuditRun)-[:HAS_PHASE]->(:Phase)
//   (:Phase)-[:HAS_FINDING]->(:Finding)
//   (:AuditRun)-[:PRODUCED]->(:Certificate)
//   (:AISystem)-[:HAS_ROPA]->(:ROPA)
//   (:AISystem)-[:RECEIVED]->(:DSARRequest)
//   (:AISystem)-[:RECEIVED]->(:ErasureRequest)
//   (:DataSubject)-[:MADE]->(:DSARRequest)
//   (:DataSubject)-[:GAVE]->(:ConsentRecord)
//   (:AISystem)-[:HAS_CONSENT]->(:ConsentRecord)
