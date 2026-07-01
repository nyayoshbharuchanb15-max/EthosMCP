import uuid
from datetime import datetime
from typing import Optional, List

from sqlalchemy import (
    String, Integer, Boolean, DateTime, ForeignKey, Text, LargeBinary, UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY as PG_ARRAY
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import text

from app.config import settings


class Base(DeclarativeBase):
    pass


class AuditRun(Base):
    __tablename__ = "audit_runs"

    run_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    system_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    system_name: Mapped[str] = mapped_column(String(200), nullable=False)
    system_version: Mapped[str] = mapped_column(String(20), nullable=False)
    org_id: Mapped[str] = mapped_column(String(100), nullable=False)
    initiated_by: Mapped[str] = mapped_column(String(200), nullable=False)
    jurisdictions: Mapped[List[str]] = mapped_column(PG_ARRAY(String), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="PENDING",
        server_default=text("'PENDING'"),
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    phases = relationship("PhaseResult", back_populates="run", cascade="all, delete-orphan")


class PhaseResult(Base):
    __tablename__ = "phase_results"

    result_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("audit_runs.run_id"), nullable=False)
    phase_number: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="PENDING")
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    artifact_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    merkle_proof: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    engine_version: Mapped[str] = mapped_column(String(20), nullable=False, default="1.0.0")

    run = relationship("AuditRun", back_populates="phases")
    findings = relationship("Finding", back_populates="phase_result", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("run_id", "phase_number", name="uq_run_phase"),
    )


class Finding(Base):
    __tablename__ = "findings"

    finding_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    result_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("phase_results.result_id"), nullable=False)
    run_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("audit_runs.run_id"), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    regulation: Mapped[str] = mapped_column(String(100), nullable=False)
    article: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    remediation: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    phase_result = relationship("PhaseResult", back_populates="findings")


class AuditArtifact(Base):
    __tablename__ = "audit_artifacts"

    artifact_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("audit_runs.run_id"), nullable=False)
    phase_number: Mapped[int] = mapped_column(Integer, nullable=False)
    artifact_type: Mapped[str] = mapped_column(String(50), nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    stored_path: Mapped[str] = mapped_column(String(500), nullable=False)
    timestamp_token: Mapped[Optional[bytes]] = mapped_column(LargeBinary, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class IssuedCertificate(Base):
    __tablename__ = "issued_certificates"

    cert_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("audit_runs.run_id"), nullable=False)
    credential_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    proof_value: Mapped[str] = mapped_column(String(200), nullable=False)
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    valid_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    revocation_reason: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)


class ErasureLog(Base):
    __tablename__ = "erasure_log"

    erasure_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dsar_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    subject_email_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    system_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    erasure_type: Mapped[str] = mapped_column(String(50), nullable=False)
    stores_affected: Mapped[List[str]] = mapped_column(PG_ARRAY(String), nullable=False)
    certificate_issued: Mapped[bool] = mapped_column(Boolean, default=False)
    performed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class RopaRecord(Base):
    __tablename__ = "ropa_records"

    ropa_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    system_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    run_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("audit_runs.run_id"), nullable=False)
    ropa_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class ConsentRecord(Base):
    __tablename__ = "consent_records"

    consent_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subject_identifier: Mapped[str] = mapped_column(String(200), nullable=False)
    system_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    consent_type: Mapped[str] = mapped_column(String(50), nullable=False)
    granted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    consent_artifacts: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)


class DsarRequest(Base):
    __tablename__ = "dsar_requests"

    dsar_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subject_email: Mapped[str] = mapped_column(String(200), nullable=False)
    request_type: Mapped[str] = mapped_column(String(50), nullable=False)
    system_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="PENDING")
    expected_completion_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


engine = create_async_engine(
    settings.database_url,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
)

async_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncSession:
    async with async_session_factory() as session:
        yield session


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Set up RLS policies for append-only enforcement
        await conn.execute(text("""
            DO $rls$
            BEGIN
                -- Audit runs: no updates or deletes
                IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'audit_runs' AND policyname = 'no_update_audit_runs') THEN
                    CREATE POLICY no_update_audit_runs ON audit_runs FOR UPDATE USING (false);
                    CREATE POLICY no_delete_audit_runs ON audit_runs FOR DELETE USING (false);
                END IF;
                -- Phase results: append-only
                IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'phase_results' AND policyname = 'no_update_phase_results') THEN
                    CREATE POLICY no_update_phase_results ON phase_results FOR UPDATE USING (false);
                    CREATE POLICY no_delete_phase_results ON phase_results FOR DELETE USING (false);
                END IF;
                -- Findings: append-only
                IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'findings' AND policyname = 'no_update_findings') THEN
                    CREATE POLICY no_update_findings ON findings FOR UPDATE USING (false);
                    CREATE POLICY no_delete_findings ON findings FOR DELETE USING (false);
                END IF;
                -- Audit artifacts: append-only
                IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'audit_artifacts' AND policyname = 'no_update_audit_artifacts') THEN
                    CREATE POLICY no_update_audit_artifacts ON audit_artifacts FOR UPDATE USING (false);
                    CREATE POLICY no_delete_audit_artifacts ON audit_artifacts FOR DELETE USING (false);
                END IF;
                -- Erasure log: append-only
                IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'erasure_log' AND policyname = 'no_update_erasure_log') THEN
                    CREATE POLICY no_update_erasure_log ON erasure_log FOR UPDATE USING (false);
                    CREATE POLICY no_delete_erasure_log ON erasure_log FOR DELETE USING (false);
                END IF;
            END;
            $rls$;
        """))
        await conn.execute(text("ALTER TABLE audit_runs ENABLE ROW LEVEL SECURITY;"))
        await conn.execute(text("ALTER TABLE phase_results ENABLE ROW LEVEL SECURITY;"))
        await conn.execute(text("ALTER TABLE findings ENABLE ROW LEVEL SECURITY;"))
        await conn.execute(text("ALTER TABLE audit_artifacts ENABLE ROW LEVEL SECURITY;"))
        await conn.execute(text("ALTER TABLE erasure_log ENABLE ROW LEVEL SECURITY;"))
