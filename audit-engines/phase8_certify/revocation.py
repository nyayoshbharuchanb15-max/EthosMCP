from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class RevocationEntry(BaseModel):
    cert_id: str
    revoked: bool
    reason: str = ""
    revoked_at: str | None = None
    index_position: int | None = None


class BitstringStatusList(BaseModel):
    context: list[str] = Field(
        default=[
            "https://www.w3.org/ns/credentials/v2",
            "https://www.w3.org/ns/credentials/status/v2",
        ],
        alias="@context",
    )
    id: str
    type: list[str] = Field(default=["BitstringStatusList"])
    statusPurpose: str = "revocation"
    encodedList: str
    ttl: int = 86400


class BitstringStatusListManager:
    def __init__(self, storage_dir: str | None = None) -> None:
        if storage_dir is None:
            storage_dir = os.path.join(os.path.dirname(__file__), "status_lists")
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        self._list_index: dict[str, RevocationEntry] = {}
        self._next_position = 0
        self._load_state()

    def _load_state(self) -> None:
        state_file = self.storage_dir / "status-list-index.json"
        if state_file.exists():
            try:
                data = json.loads(state_file.read_text("utf-8"))
                entries = data.get("entries", [])
                for entry_data in entries:
                    entry = RevocationEntry(**entry_data)
                    self._list_index[entry.cert_id] = entry
                    if entry.index_position is not None and entry.index_position >= self._next_position:
                        self._next_position = entry.index_position + 1
            except (json.JSONDecodeError, KeyError):
                pass

    def _save_state(self) -> None:
        state_file = self.storage_dir / "status-list-index.json"
        entries = []
        for entry in self._list_index.values():
            entries.append(entry.model_dump())
        state_file.write_text(
            json.dumps({"entries": entries, "updated_at": datetime.now(timezone.utc).isoformat()}, indent=2),
            "utf-8",
        )

    def manage_revocation_list(
        self,
        cert_id: str,
        revoked: bool,
        reason: str = "",
    ) -> dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat()

        if cert_id in self._list_index:
            existing = self._list_index[cert_id]
            existing.revoked = revoked
            existing.reason = reason
            existing.revoked_at = now if revoked else None
            entry = existing
        else:
            entry = RevocationEntry(
                cert_id=cert_id,
                revoked=revoked,
                reason=reason,
                revoked_at=now if revoked else None,
                index_position=self._next_position,
            )
            self._list_index[cert_id] = entry
            self._next_position += 1

        bitstring = self._build_bitstring()
        encoded_list = self._encode_bitstring(bitstring)

        status_list = BitstringStatusList(
            id=f"urn:uuid:status-list-{int(time.time())}",
            encodedList=encoded_list,
            statusPurpose="revocation",
        )

        json_path = self.storage_dir / "status-list.json"
        json_path.write_text(
            json.dumps(status_list.model_dump(by_alias=True), indent=2), "utf-8"
        )

        der_path = self.storage_dir / "status-list.der"
        der_path.write_bytes(bitstring)

        self._save_state()

        total = len(self._list_index)
        revoked_count = sum(1 for e in self._list_index.values() if e.revoked)

        return {
            "cert_id": entry.cert_id,
            "revoked": entry.revoked,
            "reason": entry.reason,
            "revoked_at": entry.revoked_at,
            "index_position": entry.index_position,
            "status_list_url": str(json_path),
            "status_list_der_url": str(der_path),
            "total_entries": total,
            "revoked_entries": revoked_count,
            "active_entries": total - revoked_count,
        }

    def _build_bitstring(self) -> bytes:
        if self._next_position == 0:
            return bytes([0])
        num_bytes = (self._next_position + 7) // 8
        bitstring = bytearray(num_bytes)
        for entry in self._list_index.values():
            if entry.revoked and entry.index_position is not None:
                byte_index = entry.index_position // 8
                bit_offset = entry.index_position % 8
                if byte_index < len(bitstring):
                    bitstring[byte_index] |= 1 << (7 - bit_offset)
        return bytes(bitstring)

    def _encode_bitstring(self, bitstring: bytes) -> str:
        import base64
        return base64.b64encode(bitstring).decode("ascii")

    def get_status(self, cert_id: str) -> RevocationEntry | None:
        return self._list_index.get(cert_id)

    def is_revoked(self, cert_id: str) -> bool:
        entry = self._list_index.get(cert_id)
        return entry.revoked if entry else False
