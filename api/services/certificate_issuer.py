from models.certificate_models import CertificateInput, CertificateResult
from datetime import datetime
import base64

class CertificateIssuerService:
    def issue(self, input_data: CertificateInput) -> CertificateResult:
        if input_data.blocker_fail_detected:
            raise ValueError("Cannot issue certificate: BLOCKER_FAIL detected in evidence store.")
            
        # Mock VC-JSON generation
        vc_json = {
            "@context": ["https://www.w3.org/ns/credentials/v2"],
            "type": ["VerifiableCredential", "AIAuditCertificate"],
            "issuer": "did:key:z6MkhaXgBZDzqzthE2t5JLafwGSGPj3NjJqxYW1D6J9d6d",
            "issuanceDate": datetime.utcnow().isoformat() + "Z",
            "credentialSubject": {
                "id": f"did:audit:{input_data.audit_session_id}",
                "auditSessionId": input_data.audit_session_id,
                "overallScore": input_data.weighted_audit_score.get("overall_score"),
                "complianceStatus": input_data.weighted_audit_score.get("compliance_status")
            },
            "proof": {
                "type": "Ed25519Signature2020",
                "proofPurpose": "assertionMethod",
                "jws": "mock_signature_placeholder"
            }
        }
        
        # Mock PDF generation
        pdf_content = b"%PDF-1.4 Mock Audit Certificate PDF content"
        pdf_base64 = base64.b64encode(pdf_content).decode('utf-8')
        
        return CertificateResult(
            vc_json=vc_json,
            pdf_base64=pdf_base64,
            issued_at=vc_json["issuanceDate"],
            explanation="W3C Verifiable Credential issued as machine-readable audit certificate per EU AI Act Art. 26.",
            regulatory_basis=["EU AI Act Art. 26", "NIST AI RMF Govern Function"]
        )
