# AI Compliance MCP Server

**Production-ready Model Context Protocol server for automated AI system auditing across 9 phases — producing W3C Verifiable Credential 2.0 certificates with EdDSA signatures, RFC 3161 timestamps, and Merkle-tree artifact chaining.**

[![CI](https://github.com/ethylan/ai-compliance-mcp-server/actions/workflows/ci.yml/badge.svg)](https://github.com/ethylan/ai-compliance-mcp-server/actions/workflows/ci.yml)
[![Release](https://github.com/ethylan/ai-compliance-mcp-server/actions/workflows/release.yml/badge.svg)](https://github.com/ethylan/ai-compliance-mcp-server/actions/workflows/release.yml)

---

## Quick Start

```bash
# 1. Clone and enter
git clone https://github.com/ethylan/ai-compliance-mcp-server.git
cd ai-compliance-mcp-server

# 2. Configure environment
cp .env.example .env
# Edit .env with your secrets

# 3. Start the full stack
make dev

# 4. Run an audit via MCP tool
curl -X POST http://localhost:3000/tools/call \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "run_phase1_register",
    "arguments": {
      "system_name": "Credit Scoring Model v2",
      "system_version": "2.1.0",
      "vendor": "Internal",
      "deployment_environment": "production",
      "jurisdictions": ["EU", "IN"]
    }
  }'
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        MCP Client                               │
│  (Claude Desktop / VS Code / Custom)                            │
└──────────────┬─────────────────────────────────────────────┬────┘
               │ stdio (localhost)            │ HTTP (network)
               ▼                             ▼
┌──────────────────────────┐    ┌──────────────────────────────┐
│   MCP Server (TS/Node)   │    │   MCP Server (TS/Node)       │
│   stdio transport        │    │   HTTP/SSE transport         │
│   No auth                │    │   OAuth 2.1 PKCE + RBAC      │
│   ────────               │    │   ────────                    │
│   run_phase1_register    │    │   Rate limited: 100/min/org  │
│   run_phase2_scope       │    │   9 phase tools               │
│   ... phase9_monitor     │    │   Health check tool           │
└──────────┬───────────────┘    └──────────┬───────────────────┘
           │ HTTP POST (phase results)      │
           ▼                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Orchestrator (Python FastAPI)                  │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────────────┐  │
│  │ State       │  │ Pipeline     │  │ Event Bus             │  │
│  │ Machine     │  │ Routers      │  │ (NATS JetStream)      │  │
│  │ ─ 9-phase   │  │ /audit       │  │ Phase complete        │  │
│  │ ─ Blocker   │  │ /certificate │  │ Drift alert           │  │
│  │   gates     │  │ /dsar        │  │ Certificate issued    │  │
│  │ ─ Reaudit   │  │ /ropa        │  │ Reaudit triggered     │  │
│  └──────┬──────┘  └──────┬───────┘  └───────────────────────┘  │
│         │                │                                      │
│         ▼                ▼                                      │
│  ┌──────────────┐  ┌──────────────┐                            │
│  │  PostgreSQL  │  │    Neo4j     │  ┌────────────┐           │
│  │  Append-only │  │  Provenance  │  │   Redis    │           │
│  │  RLS policies│  │  Graph       │  │   Cache    │           │
│  │  Erasure     │  │  Impact      │  │  Run state │           │
│  │  chain       │  │  Analysis    │  │  Subject   │           │
│  └──────────────┘  └──────────────┘  │  cache     │           │
│                                       └────────────┘           │
└─────────────────────────────────────────────────────────────────┘
           │                     │
           ▼                     ▼
┌──────────────────────┐  ┌──────────────────────────────────┐
│   Audit Engines      │  │   Crypto Layer                    │
│   (Python)           │  │   ──────────                      │
│   ────────           │  │   KMS: Vault / Local Ed25519      │
│   Phase 3 - Risk     │  │   Merkle Tree: SHA-256            │
│   Phase 4 - Privacy  │  │   DID: did:key / did:web (local)  │
│   Phase 5 - Bias     │  │   Timestamp: RFC 3161             │
│   Phase 6 - Security │  │   Revocation: BitstringStatusList │
│   Phase 7 - Explain  │  │                                    │
│   Phase 8 - Certify  │  └──────────────────────────────────┘
│   Phase 9 - Monitor  │
└──────────────────────┘
```

---

## 9-Phase Audit Pipeline

| Phase | Tool | Description | Blocking |
|-------|------|-------------|----------|
| 1 Register | `run_phase1_register` | System registration, data lineage capture, jurisdiction declaration | Yes |
| 2 Scope | `run_phase2_scope` | EU AI Act scoping decision (Art 6), jurisdictional coverage | No |
| 3 Risk | `run_phase3_risk` | Risk tier classification (Art 5-7), Annex III categorisation, conformity path | Yes |
| 4 Privacy | `run_phase4_privacy` | DPIA (GDPR Art 35), PbD (Art 25), DPDP Act Sec 5-16, RoPA (Art 30) | No |
| 5 Bias | `run_phase5_bias` | Fairlearn demographic parity, AIF360 disparate impact, intersectional | No |
| 6 Security | `run_phase6_security` | ART adversarial testing, OWASP LLM Top 10, data minimisation (Art 5(1)(c)) | No |
| 7 Explain | `run_phase7_explain` | SHAP global / LIME local explanations (Art 13-14), report builder | Yes |
| 8 Certify | `run_phase8_certify` | W3C VC 2.0 issuance, EdDSA signing, RFC 3161, Merkle anchor, status list | Gate |
| 9 Monitor | `run_phase9_monitor` | Drift detection (PSI, KS test), Prometheus metrics, reaudit trigger | No |

### Blocker Gate Logic

- **Phases 1, 3, 7**: Each can independently block progression by producing `BLOCKER`-severity findings.
- **Phase 8 (Certify)**: Enforces an **all-pass gate** — all phases 1–7 must have `PASS` status with zero `BLOCKER` findings. Phase 8 will fail if any prior phase is incomplete or has unresolved blockers.

---

## Regulatory Coverage

| Regulation | Scope | Phases |
|------------|-------|--------|
| **EU AI Act** (Regulation 2024/1689) | Risk tiers (Art 5-7), Conformity (Art 43), Transparency (Art 13-14), Biometrics | 1-9 |
| **GDPR** | DPIA (Art 35), PbD (Art 25), Erasure (Art 17), Access (Art 15), RoPA (Art 30) | 2, 4, 6, 7 |
| **DPDP Act 2023** | Consent (Sec 5-6), Notice (Sec 7), Fiduciary Obligations (Sec 8-9), Rights (Sec 11-14), Children (Sec 16) | 4 |

### GDPR Art 17 Erasure Chain

DSAR erasure requests propagate across all three data stores:

1. **PostgreSQL**: Subject identifier is hash-redacted with salt rotation (retains structural integrity for audit trail)
2. **Neo4j**: `PersonNode` and all connected edges are detach-deleted
3. **Redis**: All cache keys matching `subject:<id>:*` are flushed
4. **Artifacts**: S3/GCS paths are zeroed

A permanent `erasure_log` entry records the action with timestamp and operator identity.

---

## W3C Verifiable Credential 2.0 Certificate

Each phase 8 issuance produces a conformant VC 2.0 credential:

```json
{
  "@context": ["https://www.w3.org/ns/credentials/v2"],
  "type": ["VerifiableCredential", "AIAuditCertificate"],
  "issuer": "did:key:z6Mk...",
  "issuanceDate": "2026-07-01T12:00:00Z",
  "credentialSubject": {
    "id": "did:key:z6Mk...",
    "auditRunId": "urn:uuid:...",
    "complianceStatus": "CONFORMANT",
    "merkle_root": "sha256:abc123...",
    "rfc3161_timestamp": {
      "token_base64": "...",
      "tsa_url": "http://timestamp.digicert.com"
    }
  },
  "statusListCredential": "http://localhost:8080/status-lists/revocations-2026.json",
  "proof": {
    "type": "Ed25519Signature2020",
    "proofValue": "zEyJ0e...base58btc..."
  }
}
```

- **proofValue**: Real EdDSA signature (base58btc multibase encoded), no placeholders
- **merkle_root**: SHA-256 of all phase artifacts hashed into a Merkle tree
- **rfc3161_timestamp**: DER-encoded RFC 3161 TimeStampToken
- **statusListCredential**: Points to on-premise server only (never external)
- **DID**: `did:key` for air-gapped deployments or on-prem `did:web`

---

## Data Model

### PostgreSQL (Append-Only)

| Table | Description | RLS Policy |
|-------|-------------|------------|
| `audit_runs` | One row per audit run | org_id = current_setting('app.org_id') |
| `phase_results` | One row per phase per run | same |
| `findings` | Individual finding records | same |
| `audit_artifacts` | Phase output documents (hashed) | same |
| `issued_certificates` | W3C VC 2.0 credentials | same |
| `erasure_log` | Permanent DSAR erasure audit trail | same (no delete allowed) |
| `ropa_records` | GDPR Art 30 Records of Processing | same |
| `consent_records` | DPDP Act Sec 5 consent receipts | same |
| `dsar_requests` | Subject access / erasure requests | same |

### Neo4j (Provenance Graph)

- `AISystem` → `AuditRun` → `Phase` → `Finding`
- `Finding` -[:AFFECTS]-> `Regulation`
- `Finding` -[:HAS_IMPACT]-> `DataSubject`
- `AuditRun` -[:REAUDITS]-> `AuditRun` (selective reaudit chain)

### Redis (Cache)

- `run:<run_id>:state` — Current pipeline state
- `phase:<run_id>:<phase_number>:status` — Phase status
- `subject:<subject_id>:*` — Subject cache (flushed on DSAR erasure)

---

## Deployment

### Local (Docker Compose)

```bash
make dev     # Start all services
make down    # Stop all services
make logs    # Tail logs
make seed    # Seed Neo4j with sample data
make reset-db # Reset all databases
```

### Production (Helm/Kubernetes)

```bash
helm install ai-compliance ./deploy/helm/ai-compliance-mcp \
  --set postgres.password="..." \
  --set neo4j.password="..." \
  --set vault.token="..."
```

#### Zero Data Egress

The Helm chart deploys a `NetworkPolicy` that:
- Denies all egress to the public internet (0.0.0.0/0)
- Allows internal traffic only (RFC 1918 + cluster DNS)
- All services communicate over an internal Docker network / pod network

#### Key Security Settings

```yaml
networkPolicy:
  enabled: true
  egressRules:
    # Only internal services allowed
```

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/audit/register` | Register a new audit run |
| `POST` | `/audit/register-phase-result` | Submit phase result |
| `GET` | `/audit/{run_id}/status` | Get pipeline status |
| `POST` | `/audit/reaudit` | Trigger selective reaudit |
| `POST` | `/certificate/issue` | Issue VC 2.0 certificate |
| `POST` | `/certificate/erasure` | Issue erasure certificate |
| `POST` | `/dsar/request` | Submit DSAR (access/erasure) |
| `GET` | `/dsar/{id}/status` | Check DSAR status |
| `GET` | `/dsar/{id}/export` | Export DSAR package |
| `GET` | `/ropa/{system_id}/generate` | Generate RoPA report |
| `GET` | `/health` | Health check |

---

## Development

### Prerequisites

- Node.js 20+
- Python 3.11+
- Docker & Docker Compose
- Access to a TSA for timestamping (or use `freetsa.org`)

### Install

```bash
make install
make build
```

### Test

```bash
make test           # All tests
make test-unit      # Unit tests only
make test-integration # Integration tests only
```

### Lint & Type Check

```bash
make lint
make check
```

---

## Project Structure

```
ai-compliance-mcp-server/
├── mcp-server/              # TypeScript MCP server
│   ├── src/
│   │   ├── index.ts         # Entry point, dual-transport
│   │   ├── server.ts        # Tool registration
│   │   ├── tools/           # 9 phase tools
│   │   ├── auth/            # OAuth 2.1 PKCE + RBAC
│   │   ├── transport/       # stdio + HTTP/SSE
│   │   └── types/           # Zod schemas + interfaces
│   └── package.json
├── orchestrator/            # Python FastAPI orchestrator
│   ├── app/
│   │   ├── main.py          # FastAPI factory
│   │   ├── config.py        # Pydantic Settings
│   │   ├── logger.py        # Structured logging
│   │   ├── routers/         # /audit, /certificate, /dsar, /ropa
│   │   ├── state_machine/   # Pipeline state machine
│   │   ├── events/          # NATS JetStream pub/sub
│   │   ├── db/              # PostgreSQL, Neo4j, Redis clients
│   │   └── models/          # Pydantic response models
│   ├── tests/
│   └── requirements.txt
├── audit-engines/           # Python audit engine implementations
│   ├── phase3_risk/
│   ├── phase4_privacy/
│   ├── phase5_bias/
│   ├── phase6_security/
│   ├── phase7_explain/
│   ├── phase8_certify/
│   └── phase9_monitor/
├── crypto/                  # KMS, Merkle tree, DID
├── db/                      # Migrations, schema, seed data
├── schemas/                 # JSON-LD, tool schemas, regulatory
├── tests/                   # Shared unit + integration tests
├── deploy/                  # Docker, Compose, Helm
├── .github/workflows/       # CI + Release
├── .env.example
├── Makefile
└── README.md
```

---

## License

MIT
