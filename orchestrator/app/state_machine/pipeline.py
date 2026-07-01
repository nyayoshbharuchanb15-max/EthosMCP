import uuid
from enum import Enum
from typing import Optional
from datetime import datetime

from sqlalchemy import select, update

from app.db.postgres import async_session_factory, AuditRun, PhaseResult, Finding
from app.db.neo4j import Neo4jClient
from app.logger import logger


class PhaseStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    PASS = "PASS"
    FAIL = "FAIL"
    BLOCKER = "BLOCKER"


class PipelineStateMachine:
    PHASE_DEPENDENCIES: dict[int, list[int]] = {
        1: [],
        2: [1],
        3: [2],
        4: [3],
        5: [4],
        6: [5],
        7: [6],
        8: [1, 2, 3, 4, 5, 6, 7],
        9: [8],
    }

    @staticmethod
    async def get_phase_status(run_id: str, phase: int) -> PhaseStatus:
        async with async_session_factory() as session:
            result = await session.execute(
                select(PhaseResult.status).where(
                    PhaseResult.run_id == uuid.UUID(run_id),
                    PhaseResult.phase_number == phase,
                )
            )
            row = result.scalar_one_or_none()
            if row is None:
                return PhaseStatus.PENDING
            return PhaseStatus(row)

    @staticmethod
    async def can_execute_phase(run_id: str, phase: int) -> tuple[bool, str]:
        deps = PipelineStateMachine.PHASE_DEPENDENCIES.get(phase, [])
        for dep in deps:
            status = await PipelineStateMachine.get_phase_status(run_id, dep)
            if status != PhaseStatus.PASS:
                return False, f"Phase {dep} must be PASS before phase {phase} can execute. Current: {status.value}"
        return True, "OK"

    @staticmethod
    async def check_blocker_gate(run_id: str) -> tuple[bool, list[dict]]:
        async with async_session_factory() as session:
            result = await session.execute(
                select(Finding).where(
                    Finding.run_id == uuid.UUID(run_id),
                    Finding.severity == "BLOCKER",
                )
            )
            blocker_findings = result.scalars().all()
            blockers = [
                {
                    "finding_id": str(f.finding_id),
                    "severity": f.severity,
                    "regulation": f.regulation,
                    "article": f.article,
                    "description": f.description,
                }
                for f in blocker_findings
            ]
            return len(blockers) == 0, blockers

    @staticmethod
    async def start_phase(run_id: str, phase: int) -> Optional[str]:
        can, reason = await PipelineStateMachine.can_execute_phase(run_id, phase)
        if not can:
            logger.warning("Phase blocked by dependency", run_id=run_id, phase=phase, reason=reason)
            return reason

        async with async_session_factory() as session:
            # Create or update phase result
            existing = await session.execute(
                select(PhaseResult).where(
                    PhaseResult.run_id == uuid.UUID(run_id),
                    PhaseResult.phase_number == phase,
                )
            )
            phase_result = existing.scalar_one_or_none()
            if phase_result is None:
                phase_result = PhaseResult(
                    result_id=uuid.uuid4(),
                    run_id=uuid.UUID(run_id),
                    phase_number=phase,
                    status=PhaseStatus.IN_PROGRESS.value,
                    started_at=datetime.utcnow(),
                )
                session.add(phase_result)
            else:
                phase_result.status = PhaseStatus.IN_PROGRESS.value
                phase_result.started_at = datetime.utcnow()

            await session.commit()
            logger.info("Phase started", run_id=run_id, phase=phase)
            return None

    @staticmethod
    async def complete_phase(
        run_id: str, phase: int, status: PhaseStatus,
        artifact_hash: str, findings: list[dict],
    ) -> dict:
        async with async_session_factory() as session:
            phase_result = await session.execute(
                select(PhaseResult).where(
                    PhaseResult.run_id == uuid.UUID(run_id),
                    PhaseResult.phase_number == phase,
                )
            )
            pr = phase_result.scalar_one_or_none()
            if pr is None:
                raise ValueError(f"Phase {phase} not started for run {run_id}")

            pr.status = status.value
            pr.completed_at = datetime.utcnow()
            pr.artifact_hash = artifact_hash

            # Save findings
            for f_data in findings:
                finding = Finding(
                    finding_id=uuid.uuid4(),
                    result_id=pr.result_id,
                    run_id=uuid.UUID(run_id),
                    severity=f_data.get("severity", "LOW"),
                    regulation=f_data.get("regulation", ""),
                    article=f_data.get("article", ""),
                    description=f_data.get("description", ""),
                    remediation=f_data.get("remediation", ""),
                )
                session.add(finding)

                # Sync to Neo4j
                await Neo4jClient.create_finding_node(
                    finding_id=str(finding.finding_id),
                    severity=finding.severity,
                    regulation=finding.regulation,
                    article=finding.article,
                )
                await Neo4jClient.link_finding_to_phase(
                    finding_id=str(finding.finding_id),
                    phase_number=phase,
                    run_id=run_id,
                )

            # Update run status if blocker
            if status == PhaseStatus.BLOCKER:
                await session.execute(
                    update(AuditRun).where(AuditRun.run_id == uuid.UUID(run_id)).values(status="FAILED")
                )

            await session.commit()

            # Sync phase to Neo4j
            await Neo4jClient.create_phase_node(run_id, phase, status.value, artifact_hash)

            return {"run_id": run_id, "phase": phase, "status": status.value}

    @staticmethod
    async def trigger_reaudit(run_id: str, changed_components: list[str]) -> str:
        new_run_id = str(uuid.uuid4())
        logger.info("Triggering reaudit", original_run_id=run_id, new_run_id=new_run_id)

        async with async_session_factory() as session:
            # Get original run
            original = await session.execute(
                select(AuditRun).where(AuditRun.run_id == uuid.UUID(run_id))
            )
            orig_run = original.scalar_one_or_none()
            if orig_run is None:
                raise ValueError(f"Run {run_id} not found")

            # Create new audit run
            new_run = AuditRun(
                run_id=uuid.UUID(new_run_id),
                system_id=orig_run.system_id,
                system_name=orig_run.system_name,
                system_version=orig_run.system_version,
                org_id=orig_run.org_id,
                initiated_by="reaudit_trigger",
                jurisdictions=orig_run.jurisdictions,
                status="PENDING",
            )
            session.add(new_run)

            # Determine phase scope from Neo4j
            phase_numbers = await Neo4jClient.get_reaudit_scope(run_id, changed_components)
            reaudit_phases = phase_numbers if phase_numbers else [1, 2, 3, 4, 5, 6, 7, 8]

            for pn in reaudit_phases:
                phase_result = PhaseResult(
                    result_id=uuid.uuid4(),
                    run_id=uuid.UUID(new_run_id),
                    phase_number=pn,
                    status=PhaseStatus.PENDING.value,
                )
                session.add(phase_result)

            await session.commit()

        # Copy system node to Neo4j
        await Neo4jClient.create_system_node(
            new_run_id, str(orig_run.system_id), orig_run.system_name,
            orig_run.system_version, "",
        )

        return new_run_id
