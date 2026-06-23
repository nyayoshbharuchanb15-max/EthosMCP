from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class AuditLogBackend:
    name: str

@dataclass(frozen=True)
class PostgreSQLAuditLog(AuditLogBackend):
    def __init__(self) -> None:
        object.__setattr__(self, "name", "postgresql")

@dataclass(frozen=True)
class FileAuditLog(AuditLogBackend):
    def __init__(self) -> None:
        object.__setattr__(self, "name", "file")


def build_audit_log_backend(kind: str) -> AuditLogBackend:
    return PostgreSQLAuditLog() if kind == "postgresql" else FileAuditLog()
