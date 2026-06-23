from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class OAuthMetadata:
    issuer: str
    authorization_endpoint: str
    token_endpoint: str
    jwks_uri: str


@dataclass(frozen=True)
class AuditLogBackend:
    name: str


@dataclass(frozen=True)
class PostgreSQLAuditLog(AuditLogBackend):
    dsn: str


@dataclass(frozen=True)
class FileAuditLog(AuditLogBackend):
    path: str


@dataclass(frozen=True)
class Iso42001Mapping:
    phase_1_ropa: str = "Clause 4.1"
    ai_risk_assessment: str = "Clause 6.1.2"
    dsar_simulation: str = "Clause 8.4"
    monitoring_evaluation: str = "Clause 9.1"
    nonconformity_action: str = "Clause 10.1"


@dataclass(frozen=True)
class DpdpEvaluation:
    notice: str
    consent: str
    erasure: str
    information: str
    correction: str
    grievance: str
    nomination: str


@dataclass(frozen=True)
class DiscoveryResult:
    status: str
    detail: str
