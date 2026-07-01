import json
import base58
from typing import Tuple

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PrivateFormat,
    PublicFormat,
    NoEncryption,
)


MULTICODEC_ED25519_PUB = b"\xed\x01"


class DIDKeyGenerator:
    @staticmethod
    def generate_ed25519_keypair() -> Tuple[Ed25519PrivateKey, Ed25519PublicKey]:
        private_key = Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        return private_key, public_key

    @staticmethod
    def private_key_to_bytes(private_key: Ed25519PrivateKey) -> bytes:
        return private_key.private_bytes(
            Encoding.DER, PrivateFormat.PKCS8, NoEncryption()
        )

    @staticmethod
    def public_key_to_bytes(public_key: Ed25519PublicKey) -> bytes:
        return public_key.public_bytes(Encoding.Raw, PublicFormat.Raw)

    @staticmethod
    def build_did_document(public_key: bytes, method: str = "key") -> dict:
        if method == "key":
            multicodec_key = MULTICODEC_ED25519_PUB + public_key
            encoded = base58.b58encode(multicodec_key).decode()
            did = f"did:key:z{encoded}"
            key_id = f"{did}#keys-1"
            document = {
                "@context": [
                    "https://www.w3.org/ns/did/v1",
                    "https://w3id.org/security/suites/ed25519-2020/v1",
                ],
                "id": did,
                "verificationMethod": [
                    {
                        "id": key_id,
                        "type": "Ed25519VerificationKey2020",
                        "controller": did,
                        "publicKeyMultibase": "z" + encoded,
                    }
                ],
                "authentication": [key_id],
                "assertionMethod": [key_id],
            }
            return document
        elif method == "web":
            raise NotImplementedError("did:web document generation not yet implemented")
        else:
            raise ValueError(f"Unsupported DID method: {method}")

    @staticmethod
    def did_from_public_key(public_key: bytes) -> str:
        multicodec_key = MULTICODEC_ED25519_PUB + public_key
        encoded = base58.b58encode(multicodec_key).decode()
        return f"did:key:z{encoded}"

    @staticmethod
    def export_document_json(document: dict, indent: int = 2) -> str:
        return json.dumps(document, indent=indent)

    @staticmethod
    def generate_full_keypair(method: str = "key") -> dict:
        priv, pub = DIDKeyGenerator.generate_ed25519_keypair()
        pub_bytes = DIDKeyGenerator.public_key_to_bytes(pub)
        priv_bytes = DIDKeyGenerator.private_key_to_bytes(priv)
        document = DIDKeyGenerator.build_did_document(pub_bytes, method=method)
        return {
            "private_key": priv_bytes,
            "public_key": pub_bytes,
            "did": document["id"],
            "document": document,
        }
