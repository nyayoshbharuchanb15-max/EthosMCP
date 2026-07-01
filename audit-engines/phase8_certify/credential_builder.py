from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class CredentialSubject(BaseModel):
    id: str
    auditRunId: str
    complianceStatus: str
    merkle_root: str | None = None
    timestamp_token: str | None = None
    systemName: str | None = None
    systemVersion: str | None = None
    jurisdiction: str | None = None


class CredentialProof(BaseModel):
    type: str = "Ed25519Signature2020"
    created: str
    verificationMethod: str
    proofPurpose: str = "assertionMethod"
    proofValue: str = ""


class BuiltCredential(BaseModel):
    context: list[str] = Field(
        default=[
            "https://www.w3.org/ns/credentials/v2",
            "https://www.w3.org/ns/credentials/examples/v2",
        ],
        alias="@context",
    )
    type: list[str] = Field(default=["VerifiableCredential", "AIAuditCertificate"])
    issuer: str
    issuanceDate: str
    credentialSubject: CredentialSubject
    proof: CredentialProof | None = None


class CredentialBuilder:
    def build_credential(
        self,
        run_id: str,
        subject: dict[str, Any],
        issuer_did: str,
        include_proof: bool = True,
    ) -> BuiltCredential:
        now = datetime.now(timezone.utc).isoformat()

        credential_subject = CredentialSubject(
            id=subject.get("id", f"urn:uuid:{run_id}"),
            auditRunId=run_id,
            complianceStatus=subject.get("compliance_status", "COMPLIANT"),
            merkle_root=subject.get("merkle_root"),
            timestamp_token=subject.get("timestamp_token"),
            systemName=subject.get("system_name"),
            systemVersion=subject.get("system_version"),
            jurisdiction=subject.get("jurisdiction"),
        )

        proof = None
        if include_proof:
            proof = CredentialProof(
                created=now,
                verificationMethod=f"{issuer_did}#keys-1",
                proofPurpose="assertionMethod",
            )

        return BuiltCredential(
            issuer=issuer_did,
            issuanceDate=now,
            credentialSubject=credential_subject,
            proof=proof,
        )

    def to_jsonld(self, credential: BuiltCredential) -> dict[str, Any]:
        raw = credential.model_dump(by_alias=True)
        raw["@context"] = raw.pop("context")
        return raw
