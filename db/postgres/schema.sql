-- ============================================================================
-- AI Compliance MCP Server - PostgreSQL Schema
-- Full reference schema with tables, indexes, triggers, and RLS policies
-- ============================================================================

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================================
-- 1. AUDIT RUNS
-- ============================================================================
CREATE TABLE audit_runs (
    run_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    system_id       VARCHAR(255) NOT NULL,
    system_name     VARCHAR(512) NOT NULL,
    system_version  VARCHAR(64) NOT NULL,
    vendor          VARCHAR(255),
    status          VARCHAR(32) NOT NULL DEFAULT 'PENDING',
    audit_scope     JSONB,
    risk_level      VARCHAR(16),
    version         INTEGER NOT NULL DEFAULT 1,
    content_hash    VARCHAR(128) GENERATED ALWAYS AS (
                        encode(
                            sha256(
                                (run_id::text || system_id || system_name || system_version || COALESCE(vendor,'') || status || version::text)::bytea
                            ), 'hex'
                        )
                    ) STORED,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_audit_runs_system_id ON audit_runs (system_id);
CREATE INDEX idx_audit_runs_status ON audit_runs (status);
CREATE INDEX idx_audit_runs_created_at ON audit_runs (created_at);

-- ============================================================================
-- 2. PHASE RESULTS
-- ============================================================================
CREATE TABLE phase_results (
    id              BIGSERIAL,
    run_id          UUID NOT NULL REFERENCES audit_runs(run_id) ON DELETE CASCADE,
    phase_number    INTEGER NOT NULL,
    phase_name      VARCHAR(255) NOT NULL,
    status          VARCHAR(32) NOT NULL DEFAULT 'PENDING',
    result_data     JSONB,
    score           DOUBLE PRECISION,
    started_at      TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ,
    content_hash    VARCHAR(128) GENERATED ALWAYS AS (
                        encode(
                            sha256(
                                (run_id::text || phase_number::text || phase_name || status)::bytea
                            ), 'hex'
                        )
                    ) STORED,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (id),
    UNIQUE (run_id, phase_number)
);

CREATE INDEX idx_phase_results_run_id ON phase_results (run_id);
CREATE INDEX idx_phase_results_status ON phase_results (status);

-- ============================================================================
-- 3. FINDINGS
-- ============================================================================
CREATE TABLE findings (
    finding_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id          UUID NOT NULL REFERENCES audit_runs(run_id) ON DELETE CASCADE,
    phase_number    INTEGER NOT NULL,
    finding_type    VARCHAR(64) NOT NULL,
    severity        VARCHAR(16) NOT NULL,
    title           VARCHAR(512) NOT NULL,
    description     TEXT,
    evidence        JSONB,
    recommendation  TEXT,
    status          VARCHAR(32) NOT NULL DEFAULT 'OPEN',
    version         INTEGER NOT NULL DEFAULT 1,
    content_hash    VARCHAR(128) GENERATED ALWAYS AS (
                        encode(
                            sha256(
                                (finding_id::text || run_id::text || phase_number::text || finding_type || severity || status || version::text)::bytea
                            ), 'hex'
                        )
                    ) STORED,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_findings_run_id ON findings (run_id);
CREATE INDEX idx_findings_severity ON findings (severity);
CREATE INDEX idx_findings_type ON findings (finding_type);

-- ============================================================================
-- 4. AUDIT ARTIFACTS
-- ============================================================================
CREATE TABLE audit_artifacts (
    artifact_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id          UUID NOT NULL REFERENCES audit_runs(run_id) ON DELETE CASCADE,
    phase_number    INTEGER,
    artifact_type   VARCHAR(64) NOT NULL,
    file_name       VARCHAR(512),
    content_hash    VARCHAR(128) NOT NULL,
    content         JSONB,
    merkle_root     VARCHAR(128),
    merkle_proof    JSONB,
    storage_path    VARCHAR(1024),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_audit_artifacts_run_id ON audit_artifacts (run_id);
CREATE INDEX idx_audit_artifacts_content_hash ON audit_artifacts (content_hash);

-- ============================================================================
-- 5. ISSUED CERTIFICATES
-- ============================================================================
CREATE TABLE issued_certificates (
    cert_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id           UUID NOT NULL REFERENCES audit_runs(run_id) ON DELETE CASCADE,
    system_id        VARCHAR(255) NOT NULL,
    certificate_type VARCHAR(64) NOT NULL,
    status           VARCHAR(32) NOT NULL DEFAULT 'PENDING',
    valid_from       TIMESTAMPTZ NOT NULL,
    valid_until      TIMESTAMPTZ NOT NULL,
    metadata         JSONB,
    signature        TEXT,
    content_hash     VARCHAR(128) GENERATED ALWAYS AS (
                         encode(
                             sha256(
                                 (cert_id::text || run_id::text || system_id || certificate_type || status)::bytea
                             ), 'hex'
                         )
                     ) STORED,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_issued_certificates_run_id ON issued_certificates (run_id);
CREATE INDEX idx_issued_certificates_system_id ON issued_certificates (system_id);
CREATE INDEX idx_issued_certificates_status ON issued_certificates (status);

-- ============================================================================
-- 6. ERASURE LOG (GDPR Right to Erasure)
-- ============================================================================
CREATE TABLE erasure_log (
    id              BIGSERIAL PRIMARY KEY,
    request_id      VARCHAR(255) NOT NULL,
    system_id       VARCHAR(255) NOT NULL,
    data_subject_id VARCHAR(255) NOT NULL,
    scope           JSONB NOT NULL,
    status          VARCHAR(32) NOT NULL DEFAULT 'PENDING',
    executed_at     TIMESTAMPTZ,
    verified_at     TIMESTAMPTZ,
    evidence_hash   VARCHAR(128),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_erasure_log_request_id ON erasure_log (request_id);
CREATE INDEX idx_erasure_log_system_id ON erasure_log (system_id);
CREATE INDEX idx_erasure_log_status ON erasure_log (status);

-- ============================================================================
-- 7. ROPA RECORDS (Record of Processing Activities)
-- ============================================================================
CREATE TABLE ropa_records (
    id                   BIGSERIAL PRIMARY KEY,
    system_id            VARCHAR(255) NOT NULL,
    system_name          VARCHAR(512) NOT NULL,
    data_controller      VARCHAR(512) NOT NULL,
    data_processor       VARCHAR(512),
    processing_purpose   TEXT NOT NULL,
    data_categories      JSONB NOT NULL,
    data_subject_categories JSONB NOT NULL,
    retention_period     VARCHAR(128),
    legal_basis          VARCHAR(255) NOT NULL,
    cross_border_transfer BOOLEAN NOT NULL DEFAULT FALSE,
    safeguards           TEXT,
    version              INTEGER NOT NULL DEFAULT 1,
    created_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at           TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_ropa_records_system_id ON ropa_records (system_id);

-- ============================================================================
-- 8. CONSENT RECORDS
-- ============================================================================
CREATE TABLE consent_records (
    id              BIGSERIAL PRIMARY KEY,
    data_subject_id VARCHAR(255) NOT NULL,
    system_id       VARCHAR(255) NOT NULL,
    consent_type    VARCHAR(64) NOT NULL,
    status          VARCHAR(32) NOT NULL DEFAULT 'GRANTED',
    granted_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    revoked_at      TIMESTAMPTZ,
    expires_at      TIMESTAMPTZ,
    evidence_hash   VARCHAR(128),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_consent_records_subject_id ON consent_records (data_subject_id);
CREATE INDEX idx_consent_records_system_id ON consent_records (system_id);
CREATE INDEX idx_consent_records_status ON consent_records (status);

-- ============================================================================
-- 9. DSAR REQUESTS (Data Subject Access Requests)
-- ============================================================================
CREATE TABLE dsar_requests (
    id              BIGSERIAL PRIMARY KEY,
    request_id      VARCHAR(255) NOT NULL,
    data_subject_id VARCHAR(255) NOT NULL,
    request_type    VARCHAR(64) NOT NULL,
    status          VARCHAR(32) NOT NULL DEFAULT 'RECEIVED',
    details         JSONB,
    response_data   JSONB,
    fulfilled_at    TIMESTAMPTZ,
    deadline        TIMESTAMPTZ NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_dsar_requests_request_id ON dsar_requests (request_id);
CREATE INDEX idx_dsar_requests_subject_id ON dsar_requests (data_subject_id);
CREATE INDEX idx_dsar_requests_status ON dsar_requests (status);

-- ============================================================================
-- IMMUTABILITY TRIGGER: Reject UPDATE/DELETE on audit-critical tables
-- ============================================================================
CREATE OR REPLACE FUNCTION reject_mutation()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'Mutating table % is not allowed. This table is append-only.', TG_TABLE_NAME
        USING HINT = 'Audit tables are immutable by design. Only INSERT is permitted.';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_audit_runs_immutable
    BEFORE UPDATE OR DELETE ON audit_runs
    FOR EACH ROW EXECUTE FUNCTION reject_mutation();

CREATE TRIGGER trg_phase_results_immutable
    BEFORE UPDATE OR DELETE ON phase_results
    FOR EACH ROW EXECUTE FUNCTION reject_mutation();

CREATE TRIGGER trg_findings_immutable
    BEFORE UPDATE OR DELETE ON findings
    FOR EACH ROW EXECUTE FUNCTION reject_mutation();

CREATE TRIGGER trg_audit_artifacts_immutable
    BEFORE UPDATE OR DELETE ON audit_artifacts
    FOR EACH ROW EXECUTE FUNCTION reject_mutation();

CREATE TRIGGER trg_issued_certificates_immutable
    BEFORE UPDATE OR DELETE ON issued_certificates
    FOR EACH ROW EXECUTE FUNCTION reject_mutation();

CREATE TRIGGER trg_erasure_log_immutable
    BEFORE UPDATE OR DELETE ON erasure_log
    FOR EACH ROW EXECUTE FUNCTION reject_mutation();

-- ============================================================================
-- UPDATED_AT AUTO-TRIGGER (for mutable tables)
-- ============================================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_audit_runs_updated_at
    BEFORE UPDATE ON audit_runs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_findings_updated_at
    BEFORE UPDATE ON findings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_ropa_records_updated_at
    BEFORE UPDATE ON ropa_records
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- ROW-LEVEL SECURITY POLICIES
-- ============================================================================
ALTER TABLE audit_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE phase_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE findings ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_artifacts ENABLE ROW LEVEL SECURITY;
ALTER TABLE issued_certificates ENABLE ROW LEVEL SECURITY;
ALTER TABLE erasure_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE ropa_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE consent_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE dsar_requests ENABLE ROW LEVEL SECURITY;

-- Append-only: everyone can read and insert, but never update or delete
CREATE POLICY audit_runs_append_only ON audit_runs
    FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY phase_results_append_only ON phase_results
    FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY findings_append_only ON findings
    FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY audit_artifacts_append_only ON audit_artifacts
    FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY issued_certificates_append_only ON issued_certificates
    FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY erasure_log_append_only ON erasure_log
    FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY ropa_records_access ON ropa_records
    FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY consent_records_access ON consent_records
    FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY dsar_requests_access ON dsar_requests
    FOR ALL USING (true) WITH CHECK (true);

-- ============================================================================
-- CONTENT HASHING TRIGGER: Generate content hash on INSERT
-- ============================================================================
CREATE OR REPLACE FUNCTION set_content_hash()
RETURNS TRIGGER AS $$
BEGIN
    NEW.content_hash = encode(
        sha256(
            (COALESCE(NEW.finding_id::text, '') ||
             COALESCE(NEW.run_id::text, '') ||
             COALESCE(NEW.phase_number::text, '') ||
             COALESCE(NEW.finding_type, '') ||
             COALESCE(NEW.severity, '') ||
             COALESCE(NEW.status, '') ||
             COALESCE(NEW.version::text, '1'))::bytea
        ), 'hex'
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
