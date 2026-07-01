import hashlib
import httpx
from typing import Optional


class VaultClient:
    def __init__(self, vault_addr: str, vault_token: str, namespace: Optional[str] = None):
        self.vault_addr = vault_addr.rstrip("/")
        self.vault_token = vault_token
        self.namespace = namespace
        self._client = httpx.AsyncClient(
            base_url=self.vault_addr,
            headers=self._build_headers(),
            timeout=30.0,
        )

    def _build_headers(self) -> dict:
        headers = {"X-Vault-Token": self.vault_token}
        if self.namespace:
            headers["X-Vault-Namespace"] = self.namespace
        return headers

    async def sign(self, key_id: str, data: bytes, algorithm: str = "ED25519") -> bytes:
        digest = hashlib.sha256(data).hexdigest()
        payload = {
            "input": digest,
            "algorithm": algorithm,
            "prehashed": True,
        }
        response = await self._client.post(
            f"/v1/transit/sign/{key_id}",
            json=payload,
        )
        response.raise_for_status()
        result = response.json()
        signature_b64 = result["data"]["signature"]
        _, _, raw_sig = signature_b64.partition(":")
        return bytes.fromhex(raw_sig)

    async def verify(
        self, key_id: str, data: bytes, signature: bytes, algorithm: str = "ED25519"
    ) -> bool:
        digest = hashlib.sha256(data).hexdigest()
        sig_b64 = f"vault:v{self._get_algorithm_version(algorithm)}:{signature.hex()}"
        payload = {
            "input": digest,
            "signature": sig_b64,
            "algorithm": algorithm,
            "prehashed": True,
        }
        response = await self._client.post(
            f"/v1/transit/verify/{key_id}",
            json=payload,
        )
        response.raise_for_status()
        result = response.json()
        return result["data"]["valid"]

    def _get_algorithm_version(self, algorithm: str) -> int:
        versions = {"ED25519": 1, "ECDSA-P256": 1, "RSA-2048": 1}
        return versions.get(algorithm, 1)

    async def close(self) -> None:
        await self._client.aclose()
