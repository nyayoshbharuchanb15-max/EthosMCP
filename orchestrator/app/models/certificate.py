from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID


class VCCredentialSubject(BaseModel):
    id: str
    auditRunId: str
    complianceStatus: str
    merkle_root: Optional[str] = None
    rfc3161_timestamp: Optional[dict] = None


class VCProof(BaseModel):
    type: str = "Ed25519Signature2020"
    created: str
    verificationMethod: str
    proofPurpose: str = "assertionMethod"
    proofValue: str


class VCCredential(BaseModel):
    context: list[str] = Field(default=["https://www.w3.org/ns/credentials/v2"], alias="@context")
    type: list[str] = Field(default=["VerifiableCredential", "AIAuditCertificate"])
    issuer: str
    issuanceDate: str
    credentialSubject: VCCredentialSubject
    proof: VCProof


class CertificateIssueRequest(BaseModel):
    run_id: UUID
    proof_value: str
    merkle_root: Optional[str] = None
    timestamp_token: Optional[str] = None
    issued_at: str


class CertificateIssueResponse(BaseModel):
    cert_id: UUID
    run_id: UUID
    issued_at: str
    credential: VCCredential


class ErasureCertificateRequest(BaseModel):
    dsar_id: UUID
    subject_email_hash: str
    system_id: UUID
    stores_affected: list[str]
