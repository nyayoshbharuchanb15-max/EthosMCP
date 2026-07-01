"""Initial migration: create all compliance audit tables with RLS and immutability."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import text

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(sa.text("CREATE EXTENSION IF NOT EXISTS pgcrypto"))

    op.create_table(
        "audit_runs",
        sa.Column("run_id", sa.UUID(), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("system_id", sa.String(255), nullable=False),
        sa.Column("system_name", sa.String(512), nullable=False),
        sa.Column("system_version", sa.String(64), nullable=False),
        sa.Column("vendor", sa.String(255), nullable=True),
        sa.Column("status", sa.String(32), nullable=False, server_default="PENDING"),
        sa.Column("audit_scope", postgresql.JSONB(), nullable=True),
        sa.Column("risk_level", sa.String(16), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False, server_default=sa.text("1")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.PrimaryKeyConstraint("run_id", name=op.f("pk_audit_runs")),
    )
    op.create_index("idx_audit_runs_system_id", "audit_runs", ["system_id"])
    op.create_index("idx_audit_runs_status", "audit_runs", ["status"])
    op.create_index("idx_audit_runs_created_at", "audit_runs", ["created_at"])

    op.create_table(
        "phase_results",
        sa.Column("id", sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column("run_id", sa.UUID(), nullable=False),
        sa.Column("phase_number", sa.Integer(), nullable=False),
        sa.Column("phase_name", sa.String(255), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="PENDING"),
        sa.Column("result_data", postgresql.JSONB(), nullable=True),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["run_id"], ["audit_runs.run_id"],
            name=op.f("fk_phase_results_run_id"), ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_phase_results")),
        sa.UniqueConstraint("run_id", "phase_number", name=op.f("uq_phase_results_run_phase")),
    )
    op.create_index("idx_phase_results_run_id", "phase_results", ["run_id"])
    op.create_index("idx_phase_results_status", "phase_results", ["status"])

    op.create_table(
        "findings",
        sa.Column("finding_id", sa.UUID(), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("run_id", sa.UUID(), nullable=False),
        sa.Column("phase_number", sa.Integer(), nullable=False),
        sa.Column("finding_type", sa.String(64), nullable=False),
        sa.Column("severity", sa.String(16), nullable=False),
        sa.Column("title", sa.String(512), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("evidence", postgresql.JSONB(), nullable=True),
        sa.Column("recommendation", sa.Text(), nullable=True),
        sa.Column("status", sa.String(32), nullable=False, server_default="OPEN"),
        sa.Column("version", sa.Integer(), nullable=False, server_default=sa.text("1")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["run_id"], ["audit_runs.run_id"],
            name=op.f("fk_findings_run_id"), ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("finding_id", name=op.f("pk_findings")),
    )
    op.create_index("idx_findings_run_id", "findings", ["run_id"])
    op.create_index("idx_findings_severity", "findings", ["severity"])
    op.create_index("idx_findings_type", "findings", ["finding_type"])

    op.create_table(
        "audit_artifacts",
        sa.Column("artifact_id", sa.UUID(), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("run_id", sa.UUID(), nullable=False),
        sa.Column("phase_number", sa.Integer(), nullable=True),
        sa.Column("artifact_type", sa.String(64), nullable=False),
        sa.Column("file_name", sa.String(512), nullable=True),
        sa.Column("content_hash", sa.String(128), nullable=False),
        sa.Column("content", postgresql.JSONB(), nullable=True),
        sa.Column("merkle_root", sa.String(128), nullable=True),
        sa.Column("merkle_proof", postgresql.JSONB(), nullable=True),
        sa.Column("storage_path", sa.String(1024), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["run_id"], ["audit_runs.run_id"],
            name=op.f("fk_audit_artifacts_run_id"), ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("artifact_id", name=op.f("pk_audit_artifacts")),
    )
    op.create_index("idx_audit_artifacts_run_id", "audit_artifacts", ["run_id"])
    op.create_index("idx_audit_artifacts_content_hash", "audit_artifacts", ["content_hash"])

    op.create_table(
        "issued_certificates",
        sa.Column("cert_id", sa.UUID(), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("run_id", sa.UUID(), nullable=False),
        sa.Column("system_id", sa.String(255), nullable=False),
        sa.Column("certificate_type", sa.String(64), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="PENDING"),
        sa.Column("valid_from", sa.DateTime(timezone=True), nullable=False),
        sa.Column("valid_until", sa.DateTime(timezone=True), nullable=False),
        sa.Column("metadata", postgresql.JSONB(), nullable=True),
        sa.Column("signature", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["run_id"], ["audit_runs.run_id"],
            name=op.f("fk_issued_certificates_run_id"), ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("cert_id", name=op.f("pk_issued_certificates")),
    )
    op.create_index("idx_issued_certificates_run_id", "issued_certificates", ["run_id"])
    op.create_index("idx_issued_certificates_system_id", "issued_certificates", ["system_id"])
    op.create_index("idx_issued_certificates_status", "issued_certificates", ["status"])

    op.create_table(
        "erasure_log",
        sa.Column("id", sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column("request_id", sa.String(255), nullable=False),
        sa.Column("system_id", sa.String(255), nullable=False),
        sa.Column("data_subject_id", sa.String(255), nullable=False),
        sa.Column("scope", postgresql.JSONB(), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="PENDING"),
        sa.Column("executed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("evidence_hash", sa.String(128), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_erasure_log")),
    )
    op.create_index("idx_erasure_log_request_id", "erasure_log", ["request_id"])
    op.create_index("idx_erasure_log_system_id", "erasure_log", ["system_id"])
    op.create_index("idx_erasure_log_status", "erasure_log", ["status"])

    op.create_table(
        "ropa_records",
        sa.Column("id", sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column("system_id", sa.String(255), nullable=False),
        sa.Column("system_name", sa.String(512), nullable=False),
        sa.Column("data_controller", sa.String(512), nullable=False),
        sa.Column("data_processor", sa.String(512), nullable=True),
        sa.Column("processing_purpose", sa.Text(), nullable=False),
        sa.Column("data_categories", postgresql.JSONB(), nullable=False),
        sa.Column("data_subject_categories", postgresql.JSONB(), nullable=False),
        sa.Column("retention_period", sa.String(128), nullable=True),
        sa.Column("legal_basis", sa.String(255), nullable=False),
        sa.Column("cross_border_transfer", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("safeguards", sa.Text(), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False, server_default=sa.text("1")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_ropa_records")),
    )
    op.create_index("idx_ropa_records_system_id", "ropa_records", ["system_id"])

    op.create_table(
        "consent_records",
        sa.Column("id", sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column("data_subject_id", sa.String(255), nullable=False),
        sa.Column("system_id", sa.String(255), nullable=False),
        sa.Column("consent_type", sa.String(64), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="GRANTED"),
        sa.Column("granted_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("evidence_hash", sa.String(128), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_consent_records")),
    )
    op.create_index("idx_consent_records_subject_id", "consent_records", ["data_subject_id"])
    op.create_index("idx_consent_records_system_id", "consent_records", ["system_id"])
    op.create_index("idx_consent_records_status", "consent_records", ["status"])

    op.create_table(
        "dsar_requests",
        sa.Column("id", sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column("request_id", sa.String(255), nullable=False),
        sa.Column("data_subject_id", sa.String(255), nullable=False),
        sa.Column("request_type", sa.String(64), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="RECEIVED"),
        sa.Column("details", postgresql.JSONB(), nullable=True),
        sa.Column("response_data", postgresql.JSONB(), nullable=True),
        sa.Column("fulfilled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deadline", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_dsar_requests")),
    )
    op.create_index("idx_dsar_requests_request_id", "dsar_requests", ["request_id"])
    op.create_index("idx_dsar_requests_subject_id", "dsar_requests", ["data_subject_id"])
    op.create_index("idx_dsar_requests_status", "dsar_requests", ["status"])

    # ---- RLS Policies ----
    for table in ["audit_runs", "phase_results", "findings", "audit_artifacts",
                   "issued_certificates", "erasure_log"]:
        op.execute(sa.text(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY"))
        op.execute(sa.text(f"""
            CREATE POLICY {table}_append_only ON {table}
            FOR INSERT TO public
            WITH CHECK (true)
        """))
        op.execute(sa.text(f"""
            CREATE POLICY {table}_no_update ON {table}
            FOR UPDATE TO public
            USING (false)
        """))
        op.execute(sa.text(f"""
            CREATE POLICY {table}_no_delete ON {table}
            FOR DELETE TO public
            USING (false)
        """))

    for table in ["ropa_records", "consent_records", "dsar_requests"]:
        op.execute(sa.text(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY"))

    # ---- Immutability Triggers ----
    for table in ["audit_runs", "phase_results", "findings", "audit_artifacts",
                   "issued_certificates", "erasure_log"]:
        op.execute(sa.text(f"""
            CREATE OR REPLACE FUNCTION no_update_{table}()
            RETURNS TRIGGER AS $$
            BEGIN
                RAISE EXCEPTION 'Table % is append-only. UPDATE and DELETE are prohibited.', TG_TABLE_NAME
                    USING HINT = 'Audit tables are immutable by design. Only INSERT is permitted.';
            END;
            $$ LANGUAGE plpgsql
        """))
        op.execute(sa.text(f"""
            CREATE TRIGGER trg_{table}_immutable
            BEFORE UPDATE OR DELETE ON {table}
            FOR EACH ROW EXECUTE FUNCTION no_update_{table}()
        """))

    op.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS alembic_version (
            version_num VARCHAR(32) NOT NULL,
            CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
        )
    """))

    op.execute(sa.text("""
        INSERT INTO alembic_version (version_num) VALUES ('001_initial')
        ON CONFLICT (version_num) DO NOTHING
    """))


def downgrade() -> None:
    for table in ["erasure_log", "issued_certificates", "audit_artifacts",
                   "findings", "phase_results", "audit_runs"]:
        op.execute(sa.text(f"DROP TRIGGER IF EXISTS trg_{table}_immutable ON {table}"))
        op.execute(sa.text(f"DROP FUNCTION IF EXISTS no_update_{table}()"))
        op.execute(sa.text(f"DROP POLICY IF EXISTS {table}_no_delete ON {table}"))
        op.execute(sa.text(f"DROP POLICY IF EXISTS {table}_no_update ON {table}"))
        op.execute(sa.text(f"DROP POLICY IF EXISTS {table}_append_only ON {table}"))
        op.execute(sa.text(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY"))
    op.execute(sa.text("DROP TABLE IF EXISTS alembic_version"))
    op.drop_table("dsar_requests")
    op.drop_table("consent_records")
    op.drop_table("ropa_records")
    op.drop_table("erasure_log")
    op.drop_table("issued_certificates")
    op.drop_table("audit_artifacts")
    op.drop_table("findings")
    op.drop_table("phase_results")
    op.drop_table("audit_runs")
