import json
import time
import re
from typing import Optional

import base58


class ResolvedDocument:
    def __init__(self, document: dict, expires_at: float):
        self.document = document
        self.expires_at = expires_at

    def is_expired(self) -> bool:
        return time.time() > self.expires_at


class DIDResolver:
    def __init__(self, cache_ttl: float = 300.0):
        self._cache: dict[str, ResolvedDocument] = {}
        self._cache_ttl = cache_ttl
        self._local_web_registry: dict[str, dict] = {}

    @staticmethod
    def _decode_multibase_base58btc(encoded: str) -> bytes:
        if encoded.startswith("z"):
            encoded = encoded[1:]
        return base58.b58decode(encoded)

    @staticmethod
    def _extract_key_from_did_key(did: str) -> Optional[bytes]:
        prefix = "did:key:"
        if not did.startswith(prefix):
            return None
        encoded = did[len(prefix):]
        try:
            raw = DIDResolver._decode_multibase_base58btc(encoded)
            return raw
        except Exception:
            return None

    @staticmethod
    def _build_did_key_document(did: str, public_key_bytes: bytes) -> dict:
        key_id = f"{did}#keys-1"
        return {
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
                    "publicKeyMultibase": "z" + base58.b58encode(public_key_bytes).decode(),
                }
            ],
            "authentication": [key_id],
            "assertionMethod": [key_id],
        }

    def register_local_web_did(self, did: str, document: dict) -> None:
        if not did.startswith("did:web:"):
            raise ValueError("Only did:web DIDs can be registered locally")
        self._local_web_registry[did] = document

    def _resolve_did_web(self, did: str) -> Optional[dict]:
        return self._local_web_registry.get(did)

    def resolve(self, did: str) -> dict:
        cached = self._cache.get(did)
        if cached and not cached.is_expired():
            return cached.document

        if did.startswith("did:key:"):
            key_bytes = self._extract_key_from_did_key(did)
            if key_bytes is None:
                raise ValueError(f"Invalid did:key identifier: {did}")
            doc = self._build_did_key_document(did, key_bytes)
        elif did.startswith("did:web:"):
            doc = self._resolve_did_web(did)
            if doc is None:
                raise ValueError(f"Unknown local did:web DID: {did}")
        else:
            raise ValueError(f"Unsupported DID method: {did}")

        resolved = ResolvedDocument(doc, time.time() + self._cache_ttl)
        self._cache[did] = resolved
        return doc

    def resolve_with_metadata(self, did: str) -> dict:
        document = self.resolve(did)
        return {
            "didResolutionMetadata": {"contentType": "application/did+ld+json"},
            "didDocument": document,
            "didDocumentMetadata": {},
        }

    def clear_cache(self) -> None:
        self._cache.clear()

    def invalidate_cache(self, did: str) -> None:
        self._cache.pop(did, None)
