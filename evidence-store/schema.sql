-- AI Governance Evidence Store Schema
-- Implements immutable audit trails

CREATE TABLE IF NOT EXISTS audit_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    system_name TEXT NOT NULL,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    status TEXT NOT NULL DEFAULT 'STARTED'
);

CREATE TABLE IF NOT EXISTS phase_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES audit_sessions(id),
    phase_number INTEGER NOT NULL,
    tool_name TEXT NOT NULL,
    result_json JSONB NOT NULL,
    explanation TEXT NOT NULL,
    regulatory_basis TEXT[] NOT NULL,
    written_at TIMESTAMPTZ DEFAULT NOW(),
    content_hash TEXT
);

CREATE TABLE IF NOT EXISTS certificates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES audit_sessions(id),
    vc_json JSONB NOT NULL,
    pdf_base64 TEXT NOT NULL,
    issued_at TIMESTAMPTZ DEFAULT NOW(),
    revoked BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS drift_alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES audit_sessions(id),
    detected_at TIMESTAMPTZ DEFAULT NOW(),
    metric TEXT NOT NULL,
    threshold FLOAT NOT NULL,
    actual_value FLOAT NOT NULL,
    reaudit_triggered BOOLEAN DEFAULT FALSE
);

-- Immutability Triggers
CREATE OR REPLACE FUNCTION reject_update_delete()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'Table is immutable. UPDATE and DELETE operations are prohibited.';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER phase_results_immutable
BEFORE UPDATE OR DELETE ON phase_results
FOR EACH ROW EXECUTE FUNCTION reject_update_delete();

-- Content Hashing Trigger
CREATE OR REPLACE FUNCTION compute_content_hash()
RETURNS TRIGGER AS $$
BEGIN
    NEW.content_hash := encode(sha256(NEW.result_json::text::bytea), 'hex');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER phase_results_hash
BEFORE INSERT ON phase_results
FOR EACH ROW EXECUTE FUNCTION compute_content_hash();
