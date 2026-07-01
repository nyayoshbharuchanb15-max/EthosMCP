import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.db.postgres import async_session_factory, AuditRun, PhaseResult, Finding, RopaRecord
from app.logger import logger

router = APIRouter(prefix="/ropa", tags=["ropa"])


@router.get("/{system_id}/generate")
async def generate_ropa(system_id: str):
    """
    Generate a GDPR Art. 30 Record of Processing Activities.
    Pulls data from the most recent audit run for the system.
    """
    try:
        sys_uuid = uuid.UUID(system_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid system_id")

    async with async_session_factory() as session:
        # Find the most recent audit run for this system
        run = await session.execute(
            select(AuditRun)
            .where(AuditRun.system_id == sys_uuid)
            .order_by(AuditRun.created_at.desc())
            .limit(1)
        )
        run_record = run.scalar_one_or_none()
        if run_record is None:
            raise HTTPException(status_code=404, detail="No audit run found for this system")

        # Pull all phase results
        phases = await session.execute(
            select(PhaseResult).where(PhaseResult.run_id == run_record.run_id)
        )
        phase_results = phases.scalars().all()

        # Pull findings for risk context
        findings = await session.execute(
            select(Finding).where(Finding.run_id == run_record.run_id)
        )
        all_findings = findings.scalars().all()

        # Build ROPA record per Art 30(1)
        ropa: dict = {
            "controller": {
                "name": "Organization Name (configure in .env)",
                "contact": "dpo@organization.com",
                "representative": None,
            },
            "processing_activities": [
                {
                    "purpose": "AI system compliance auditing and governance",
                    "description": "Systematic evaluation of AI systems for regulatory compliance across EU AI Act, GDPR, and DPDP Act frameworks",
                    "data_subject_categories": list(set(
                        r.jurisdictions for r in [run_record]
                    )),
                    "data_categories": [
                        "System metadata",
                        "Processing logs",
                        "Audit findings",
                        "Compliance evidence",
                    ],
                    "recipient_categories": ["Internal compliance team", "Data Protection Officer", "External auditor (if applicable)"],
                    "third_country_transfers": [],
                    "retention_period": "7 years (statutory limitation period)",
                    "technical_organisational_measures": [],
                }
            ],
            "system": {
                "id": system_id,
                "name": run_record.system_name,
                "version": run_record.system_version,
                "jurisdictions": run_record.jurisdictions,
            },
            "audit": {
                "run_id": str(run_record.run_id),
                "status": run_record.status,
                "phases_completed": sum(1 for p in phase_results if p.status == "PASS"),
                "total_phases": len(phase_results),
                "generated_at": datetime.utcnow().isoformat(),
            },
        }

        # Extract technical measures from Phase 6 (security) findings
        security_findings = [f for f in all_findings if "security" in f.article.lower() or "Art. 15" in f.article]
        for sf in security_findings:
            ropa["processing_activities"][0]["technical_organisational_measures"].append(sf.remediation)

        # Check for third country transfers (should be none in zero-egress)
        for p in phase_results:
            if p.phase_number == 4 and p.status == "PASS":
                ropa["processing_activities"][0]["third_country_transfers"] = ["None — zero-data-egress architecture"]

        # Persist ROPA record
        ropa_record = RopaRecord(
            ropa_id=uuid.uuid4(),
            system_id=sys_uuid,
            run_id=run_record.run_id,
            ropa_json=ropa,
        )
        session.add(ropa_record)
        await session.commit()

    logger.info("ROPA generated", system_id=system_id, run_id=str(run_record.run_id))

    return ropa
