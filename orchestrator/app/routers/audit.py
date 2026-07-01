import uuid
from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.db.postgres import async_session_factory, AuditRun, PhaseResult, Finding, AuditArtifact
from app.db.neo4j import Neo4jClient
from app.db.redis import RedisClient
from app.state_machine.pipeline import PipelineStateMachine, PhaseStatus
from app.models.run import BlockerFinding

router = APIRouter(prefix="/audit", tags=["audit"])


@router.post("/register", status_code=201)
async def register_audit_run(payload: dict):
    """Phase 1: Register an AI system for auditing."""
    run_id = payload.get("run_id", str(uuid.uuid4()))
    system_id = payload.get("system_id")

    async with async_session_factory() as session:
        run = AuditRun(
            run_id=uuid.UUID(run_id),
            system_id=uuid.UUID(system_id),
            system_name=payload.get("system_name", ""),
            system_version=payload.get("system_version", "1.0.0"),
            org_id=payload.get("org_id", "default"),
            initiated_by=payload.get("requested_by", "unknown"),
            jurisdictions=payload.get("jurisdictions", []),
            status="REGISTERED",
        )
        session.add(run)

        # Create phase 1 as PENDING
        phase1 = PhaseResult(
            result_id=uuid.uuid4(),
            run_id=uuid.UUID(run_id),
            phase_number=1,
            status=PhaseStatus.PENDING.value,
        )
        session.add(phase1)
        await session.commit()

    # Sync to Neo4j
    await Neo4jClient.create_system_node(
        run_id, system_id, payload.get("system_name", ""),
        payload.get("system_version", "1.0.0"), payload.get("vendor", ""),
    )

    # Cache run state
    await RedisClient.cache_run_state(run_id, {"status": "REGISTERED", "phase": 1})

    return {
        "run_id": run_id,
        "status": "REGISTERED",
        "message": "Audit run registered successfully",
    }


@router.post("/register-phase-result")
async def register_phase_result(payload: dict):
    """Register a phase result from MCP tools."""
    run_id = payload.get("run_id")
    phase = payload.get("phase")
    status = payload.get("phase_result", PhaseStatus.PASS.value)
    findings = payload.get("findings", [])
    artifact_hash = payload.get("artifact_hash", "")

    result = await PipelineStateMachine.complete_phase(
        run_id=run_id,
        phase=phase,
        status=PhaseStatus(status),
        artifact_hash=artifact_hash,
        findings=findings,
    )

    return result


@router.get("/{run_id}/status")
async def get_audit_status(run_id: str):
    """Get full audit status including all phases and any blocker findings."""
    try:
        run_uuid = uuid.UUID(run_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid run_id")

    async with async_session_factory() as session:
        run = await session.execute(select(AuditRun).where(AuditRun.run_id == run_uuid))
        run_record = run.scalar_one_or_none()
        if run_record is None:
            raise HTTPException(status_code=404, detail="Audit run not found")

        phases_result = await session.execute(
            select(PhaseResult).where(PhaseResult.run_id == run_uuid).order_by(PhaseResult.phase_number)
        )
        phases = phases_result.scalars().all()

        blocker_findings_result = await session.execute(
            select(Finding).where(Finding.run_id == run_uuid, Finding.severity == "BLOCKER")
        )
        blockers = blocker_findings_result.scalars().all()

        artifacts_result = await session.execute(
            select(AuditArtifact).where(AuditArtifact.run_id == run_uuid)
        )
        artifacts = artifacts_result.scalars().all()

    return {
        "run_id": run_id,
        "status": run_record.status,
        "phases": {p.phase_number: p.status for p in phases},
        "blocker_findings": [
            BlockerFinding(
                finding_id=f.finding_id,
                severity="BLOCKER",
                regulation=f.regulation,
                article=f.article,
                description=f.description,
            )
            for f in blockers
        ],
        "artifacts": [
            {"artifact_id": str(a.artifact_id), "phase_number": a.phase_number,
             "type": a.artifact_type, "content_hash": a.content_hash}
            for a in artifacts
        ],
    }


@router.post("/reaudit")
async def trigger_reaudit(payload: dict):
    """Trigger a reaudit based on changed components (e.g., drift detected)."""
    run_id = payload.get("run_id")
    changed_components = payload.get("changed_components", [])

    new_run_id = await PipelineStateMachine.trigger_reaudit(run_id, changed_components)

    return {
        "original_run_id": run_id,
        "new_run_id": new_run_id,
        "status": "REAUDIT_TRIGGERED",
    }
