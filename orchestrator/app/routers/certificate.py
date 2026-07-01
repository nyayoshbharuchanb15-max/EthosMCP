import uuid
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.db.postgres import async_session_factory, IssuedCertificate, AuditRun, ErasureLog
from app.models.certificate import (
    CertificateIssueRequest, CertificateIssueResponse,
    VCCredential, VCCredentialSubject, VCProof,
    ErasureCertificateRequest,
)
from app.state_machine.pipeline import PipelineStateMachine
from app.logger import logger

router = APIRouter(prefix="/certificate", tags=["certificate"])


@router.post("/issue", status_code=201)
async def issue_certificate(req: CertificateIssueRequest):
    """Issue a W3C Verifiable Credential 2.0 for a completed audit run."""
    # Check blocker gate
    clear, blockers = await PipelineStateMachine.check_blocker_gate(str(req.run_id))
    if not clear:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot issue certificate: {len(blockers)} blocker finding(s) exist",
        )

    async with async_session_factory() as session:
        run = await session.execute(select(AuditRun).where(AuditRun.run_id == req.run_id))
        run_record = run.scalar_one_or_none()
        if run_record is None:
            raise HTTPException(status_code=404, detail="Audit run not found")

        issuer_did = "did:key:z6MkhaXgBZDzqzthE2t5JLafwGSGPj3NjJqxYW1D6J9d6d"

        credential = VCCredential(
            context=["https://www.w3.org/ns/credentials/v2"],
            type=["VerifiableCredential", "AIAuditCertificate"],
            issuer=issuer_did,
            issuanceDate=req.issued_at,
            credentialSubject=VCCredentialSubject(
                id=f"did:audit:{req.run_id}",
                auditRunId=str(req.run_id),
                complianceStatus="Compliant",
                merkle_root=req.merkle_root,
                rfc3161_timestamp={
                    "token_base64": req.timestamp_token,
                    "tsa_url": "http://timestamp.yourorg.internal",
                } if req.timestamp_token else None,
            ),
            proof=VCProof(
                created=req.issued_at,
                verificationMethod=f"{issuer_did}#{issuer_did.split(':')[-1]}",
                proofValue=req.proof_value,
            ),
        )

        cert = IssuedCertificate(
            cert_id=uuid.uuid4(),
            run_id=req.run_id,
            credential_json=credential.model_dump(by_alias=True),
            proof_value=req.proof_value,
            issued_at=datetime.utcnow(),
            valid_until=datetime.utcnow() + timedelta(days=365),
        )
        session.add(cert)
        await session.commit()

        # Update run status
        run_record.status = "CERTIFIED"

        await session.commit()
        cert_id = cert.cert_id

    logger.info("Certificate issued", run_id=str(req.run_id), cert_id=str(cert_id))

    return CertificateIssueResponse(
        cert_id=cert_id,
        run_id=req.run_id,
        issued_at=req.issued_at,
        credential=credential,
    )


@router.post("/erasure", status_code=201)
async def issue_erasure_certificate(req: ErasureCertificateRequest):
    """Issue an erasure certificate for GDPR Art. 17 compliance."""
    async with async_session_factory() as session:
        erasure_log = ErasureLog(
            erasure_id=uuid.uuid4(),
            dsar_id=req.dsar_id,
            subject_email_hash=req.subject_email_hash,
            system_id=req.system_id,
            erasure_type="GDPR_ART_17",
            stores_affected=req.stores_affected,
            certificate_issued=True,
        )
        session.add(erasure_log)
        await session.commit()

    return {
        "status": "ERASURE_CERTIFICATE_ISSUED",
        "dsar_id": str(req.dsar_id),
        "stores_affected": req.stores_affected,
    }
