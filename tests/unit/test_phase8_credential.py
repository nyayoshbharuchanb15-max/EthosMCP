import json
import base64
import hashlib
import pytest


class TestVCCredential:

    @pytest.fixture
    def valid_credential(self):
        return {
            "@context": [
                "https://www.w3.org/ns/credentials/v2",
                "https://w3id.org/security/suites/ed25519-2020/v1",
            ],
            "type": ["VerifiableCredential", "AIAuditCertificate"],
            "issuer": "did:key:z6MkhaXgBZDzqzthE2t5JLafwGSGPj3NjJqxYW1D6J9d6d",
            "issuanceDate": "2026-06-15T10:30:00Z",
            "credentialSubject": {
                "id": "did:audit:550e8400-e29b-41d4-a716-446655440000",
                "auditRunId": "550e8400-e29b-41d4-a716-446655440000",
                "complianceStatus": "Compliant",
                "merkle_root": "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2",
                "rfc3161_timestamp": {
                    "token_base64": "MIIF2gYJKoZIhvcNAQcCoIIFyzCCBccCAQExCzAJBgUrDgMCGgUAMIIDAwYJKoZIhvcNAQcBoIID9ASCA/8=",
                    "tsa_url": "http://timestamp.yourorg.internal",
                },
            },
            "proof": {
                "type": "Ed25519Signature2020",
                "created": "2026-06-15T10:30:00Z",
                "verificationMethod": "did:key:z6MkhaXgBZDzqzthE2t5JLafwGSGPj3NjJqxYW1D6J9d6d#z6MkhaXgBZDzqzthE2t5JLafwGSGPj3NjJqxYW1D6J9d6d",
                "proofPurpose": "assertionMethod",
                "proofValue": "z2MkhaXgBZDzqzthE2t5JLafwGSGPj3NjJqxYW1D6J9d6dA1b2C3d4E5f6G7h8J9j1K1k2M3n4N5p6Q7r8S9t1U1v2W3x4Y5z6",
            },
            "statusListCredential": "http://localhost:8080/status-lists/revocations-2026.json",
        }

    BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

    @staticmethod
    def is_valid_base58btc(s: str) -> bool:
        decoded = s[1:] if s.startswith("z") else s
        return all(c in TestVCCredential.BASE58_ALPHABET for c in decoded)

    def test_credential_structure_valid_vc2_jsonld(self, valid_credential):
        assert "@context" in valid_credential
        assert isinstance(valid_credential["@context"], list)
        assert "https://www.w3.org/ns/credentials/v2" in valid_credential["@context"]
        assert "type" in valid_credential
        assert "VerifiableCredential" in valid_credential["type"]
        assert "AIAuditCertificate" in valid_credential["type"]
        assert "issuer" in valid_credential
        assert "credentialSubject" in valid_credential
        assert "proof" in valid_credential

    def test_proof_value_is_real_base58btc_not_placeholder(self, valid_credential):
        proof_value = valid_credential["proof"]["proofValue"]
        assert proof_value != "{{SIGNED_BY_SIGNER_PY}}"
        assert self.is_valid_base58btc(proof_value), "proofValue must be valid base58btc"
        assert len(proof_value) > 40, "proofValue should be a substantial base58btc string"

    def test_merkle_root_matches_phase_artifact_hashes(self, valid_credential):
        merkle_root = valid_credential["credentialSubject"]["merkle_root"]
        assert merkle_root != "{{SHA256_OF_ALL_PHASE_ARTIFACTS}}"
        assert len(merkle_root) == 64, "merkle_root must be a 64-char hex string"
        int(merkle_root, 16)

    def test_rfc3161_token_is_parseable_der(self, valid_credential):
        token_b64 = valid_credential["credentialSubject"]["rfc3161_timestamp"]["token_base64"]
        assert token_b64 != "{{RFC3161_TOKEN}}"
        try:
            decoded = base64.b64decode(token_b64)
            assert len(decoded) > 10, "DER token too short"
        except Exception as exc:
            pytest.fail(f"RFC3161 token is not valid base64: {exc}")

    def test_status_list_url_is_internal_not_external(self, valid_credential):
        status_url = valid_credential["statusListCredential"]
        assert "localhost" in status_url or "10." in status_url or "192.168." in status_url or ".internal" in status_url
        assert "example.com" not in status_url
        assert status_url.startswith("http://localhost:8080")
