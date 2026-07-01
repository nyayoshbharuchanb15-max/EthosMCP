from __future__ import annotations

import asyncio
import hashlib
import logging
from typing import Any

logger = logging.getLogger(__name__)

FREETSA_URL = "http://freetsa.org:6018"


class RFC3161Timestamper:
    def __init__(self, tsa_url: str | None = None) -> None:
        self.tsa_url = tsa_url or FREETSA_URL
        self._crypto_available = False
        try:
            from cryptography import x509  # noqa: F401
            from cryptography.hazmat.primitives import hashes  # noqa: F401
            self._crypto_available = True
        except ImportError:
            logger.warning("cryptography library not available. Install with: pip install cryptography")

    async def timestamp_artifact(self, data: bytes) -> bytes:
        digest = hashlib.sha256(data).digest()
        timestamp_req = self._build_timestamp_request(digest)

        try:
            response = await self._send_request(timestamp_req)
            return self._parse_response(response)
        except Exception as e:
            logger.warning(f"Primary TSA ({self.tsa_url}) failed: {e}")
            if self.tsa_url != FREETSA_URL:
                logger.info("Falling back to freetsa.org")
                fallback = RFC3161Timestamper(tsa_url=FREETSA_URL)
                return await fallback.timestamp_artifact(data)
            raise RuntimeError("All TSA endpoints failed") from e

    def _build_timestamp_request(self, digest: bytes) -> bytes:
        import struct

        _hashlib_oid = hashlib.sha256
        oid_bytes = bytes([0x60, 0x86, 0x48, 0x01, 0x65, 0x03, 0x04, 0x02, 0x01])

        req_parts = bytearray()
        req_parts.append(0x30)
        req_parts.extend(struct.pack(">H", 0 + 2 + 2 + len(oid_bytes) + 2 + len(digest) + 4 + 2 + 1))

        req_parts.append(0x02)
        req_parts.append(0x01)
        req_parts.append(0x01)

        req_parts.append(0x30)
        req_parts.extend(struct.pack(">H", len(oid_bytes) + 2 + len(digest) + 2))

        req_parts.append(0x30)
        req_parts.extend(struct.pack(">H", len(oid_bytes) + 2))

        req_parts.append(0x06)
        req_parts.append(len(oid_bytes))
        req_parts.extend(oid_bytes)

        req_parts.append(0x04)
        req_parts.append(len(digest))
        req_parts.extend(digest)

        req_parts.append(0x01)
        req_parts.append(0x01)
        req_parts.append(0xFF)

        outer = bytearray()
        outer.append(0x30)
        outer.extend(struct.pack(">H", len(req_parts)))
        outer.extend(req_parts)

        return bytes(outer)

    async def _send_request(self, timestamp_req: bytes) -> bytes:
        try:
            import httpx
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.tsa_url,
                    content=timestamp_req,
                    headers={"Content-Type": "application/timestamp-query"},
                )
                response.raise_for_status()
                return response.content
        except ImportError:
            import urllib.request
            loop = asyncio.get_event_loop()
            req = urllib.request.Request(
                self.tsa_url,
                data=timestamp_req,
                headers={"Content-Type": "application/timestamp-query"},
            )
            result = await loop.run_in_executor(
                None, lambda: urllib.request.urlopen(req, timeout=30).read()
            )
            return result

    def _parse_response(self, response: bytes) -> bytes:
        if not response:
            raise ValueError("Empty response from TSA")
        if len(response) < 20:
            raise ValueError(f"Response too short ({len(response)} bytes) — invalid TST")
        return response

    @staticmethod
    def get_timestamp_info(tst_data: bytes) -> dict[str, Any]:
        return {
            "token_bytes": len(tst_data),
            "token_hex": tst_data.hex()[:64] + "..." if len(tst_data) > 32 else tst_data.hex(),
            "algorithm": "SHA-256",
            "protocol": "RFC 3161",
        }
