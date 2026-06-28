import json
from datetime import datetime

class VCIssuer:
    """
    Issues W3C Verifiable Credentials 2.0
    """
    def __init__(self, issuer_did: str):
        self.issuer_did = issuer_did

    def create_credential(self, subject_id: str, claims: dict) -> dict:
        vc = {
            "@context": ["https://www.w3.org/ns/credentials/v2"],
            "type": ["VerifiableCredential", "AIAuditCertificate"],
            "issuer": self.issuer_did,
            "issuanceDate": datetime.utcnow().isoformat() + "Z",
            "credentialSubject": {
                "id": subject_id,
                **claims
            },
            "proof": {
                "type": "Ed25519Signature2020",
                "proofPurpose": "assertionMethod",
                "jws": "placeholder_signature"
            }
        }
        return vc

if __name__ == "__main__":
    issuer = VCIssuer("did:key:z6MkhaXgBZDzqzthE2t5JLafwGSGPj3NjJqxYW1D6J9d6d")
    print(json.dumps(issuer.create_credential("did:audit:123", {"score": 95}), indent=2))
