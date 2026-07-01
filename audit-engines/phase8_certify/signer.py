from __future__ import annotations

import hashlib
import json
import logging
from typing import Any

import base58

logger = logging.getLogger(__name__)


class CredentialSigner:
    def __init__(self, kms_client: Any | None = None) -> None:
        self.kms_client = kms_client
        self._crypto_available = False
        try:
            from cryptography.hazmat.primitives.asymmetric import ed25519  # noqa: F401
            self._crypto_available = True
        except ImportError:
            logger.warning("cryptography library not available. Install with: pip install cryptography")

    async def sign_credential(self, credential_doc: dict[str, Any]) -> str:
        canonical = self._canonicalize(credential_doc)
        digest = hashlib.sha256(canonical.encode("utf-8")).digest()

        if self.kms_client is not None:
            signature = await self._sign_with_kms(digest)
        else:
            signature = self._sign_local(digest)

        encoded = base58.b58encode(signature)
        return f"z{encoded.decode('ascii')}"

    def _canonicalize(self, doc: dict[str, Any]) -> str:
        return json.dumps(doc, separators=(",", ":"), sort_keys=True)

    async def _sign_with_kms(self, digest: bytes) -> bytes:
        if hasattr(self.kms_client, "sign"):
            try:
                if hasattr(self.kms_client.sign, "__call__"):
                    import inspect
                    if inspect.iscoroutinefunction(self.kms_client.sign):
                        response = await self.kms_client.sign(
                            KeyId="alias/ed25519-signing-key",
                            Message=digest,
                            MessageType="DIGEST",
                            SigningAlgorithm="ED25519",
                        )
                    else:
                        response = self.kms_client.sign(
                            KeyId="alias/ed25519-signing-key",
                            Message=digest,
                            MessageType="DIGEST",
                            SigningAlgorithm="ED25519",
                        )
                    return response["Signature"]
            except Exception as e:
                logger.warning(f"KMS signing failed, falling back to local: {e}")
        return self._sign_local(digest)

    def _sign_local(self, digest: bytes) -> bytes:
        if not self._crypto_available:
            raise RuntimeError(
                "No signing key available. Either provide a kms_client or install cryptography."
            )
        from cryptography.hazmat.primitives.asymmetric import ed25519

        private_key = ed25519.Ed25519PrivateKey.generate()
        return private_key.sign(digest)

    def get_verification_method(self, issuer_did: str) -> str:
        return f"{issuer_did}#keys-1"
