# EthosMCP: Zero-Trust AI Governance & Compliance Auditing Framework

**Architect & Policy Lead:** Nyayosh Bharucha (BBA LLB Hons, Principal AI Governance Architect)
**Status:** Functional Prototype & Open-Source Architectural Blueprint

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![Compliance](https://img.shields.io/badge/Compliance-GDPR%20%7C%20DPDP%20%7C%20EU%20AI%20Act-success.svg)](#)

---

## 📌 Executive Summary

Modern AI systems process vast quantities of personal data across geographic boundaries and complex organizational silos. Traditional, manual compliance audits—relying on spreadsheets and interviews—are dangerously slow, fragmented, and incapable of verifying the true state of high-velocity data pipelines.

**EthosMCP** bridges the gap between high-level regulatory frameworks (EU AI Act, GDPR, DPDP Act) and production-grade engineering realities.

Designed by a Legal & Compliance Specialist, this repository serves as a **vendor-neutral architectural specification and functional prototype** for automated, zero-trust ethical AI governance. It provides a deterministic methodology for engineering and compliance teams to collaborate, ensuring that privacy, security, and accountability are mathematically embedded into the system architecture.

### 💡 The Value Proposition
*   **Operationalized Law:** Translates statutory provisions (e.g., GDPR Art. 30, DPDP Sec. 10) into machine-readable, executable compliance vectors.
*   **Zero-Trust Auditing:** Auditors query metadata and schemas—never raw personal data—eliminating the audit process itself as a vector for data exposure.
*   **Cryptographic Evidence:** Generates immutable, cryptographically signed audit trails suitable for regulatory submission and non-repudiation.
*   **Deterministic DSAR Simulation:** Proves compliance by actively simulating Data Subject Access Requests (DSARs) to verify erasure latency across all system layers.

---

## 🔑 Design Principles

Three structural guarantees are enforced at the architectural level — not by policy documentation, but by code:

*   **Zero-Trust Audit Boundary:** The MCP server never accesses, stores, or transmits raw personal data. All tool results return only schema metadata, aggregated compliance vectors, and cryptographic state hashes. The audit process itself cannot become a data-exposure event.
*   **Cryptographic Non-Repudiation:** Every audit report carries an HMAC-SHA256 response signature over the result payload and a SHA-256 hash of the data state at query time. Neither the auditor nor the auditee can retroactively alter a report without breaking the signature.
*   **Metadata-Only Posture:** All four audit phases operate in read-only mode. No tool invocation can mutate the state of an underlying source system.

---

## 🏛️ Architectural Blueprint

EthosMCP utilizes the Model Context Protocol (MCP) to establish a secure, read-only interface between the auditor and the organization's infrastructure.

```mermaid
graph TD
    subgraph Auditor Environment
        A[AI Auditor Client] -->|MCP Queries| B(EthosMCP Server)
    end

    subgraph Organizational Infrastructure Boundary
        B -->|Read-Only Metadata Queries| C{Data Stores & Registries}
        C -->|Phase 1| D[ROPA Registry]
        C -->|Phase 2| E[Data Flow Topology]
        C -->|Phase 3| F[Consent DB]
        C -->|Phase 4| G[Infrastructure Config]
    end

    subgraph Cryptographic Verification
        B --> H[Hash Generator]
        H --> I[HMAC Signer]
        I --> J[(Immutable Audit Log)]
    end

    B -.->|Signed Audit Report| A

    classDef boundary fill:#f9f9f9,stroke:#333,stroke-width:2px;
    class Auditor Environment,Organizational Infrastructure Boundary boundary;
```

---

## 📖 Core Documentation

To fully understand the strategic and technical depth of this framework, please review the core documentation:

1.  **[FRAMEWORK_GOVERNANCE.md](./FRAMEWORK_GOVERNANCE.md):** The strategic mandate detailing ethical design choices, zero-trust data handling policies, and alignment with ISO/IEC 42001.
2.  **[AUDITING_FRAMEWORK.md](./AUDITING_FRAMEWORK.md):** The technical blueprint demonstrating the four-phase deterministic audit methodology, cryptographic verification, and DSAR simulation.
3.  **[docs/architecture.md](./docs/architecture.md):** A deeper dive into the specific Python components, FastMCP integration, and Pydantic schemas.
4.  **[docs/compliance_mapping.md](./docs/compliance_mapping.md):** The explicit mapping of statutory legal provisions to programmatic Python audit vectors.

---

## ⚙️ The Four-Phase Audit Workflow

EthosMCP executes compliance audits through a deterministic, sequential protocol. Each phase issues a cryptographic token that gates the next phase — a failed phase halts the chain by default.

| Phase | Name | What it audits | Statutory anchors |
| :---: | :--- | :--- | :--- |
| 1 | **Governance & ROPA Alignment** | Data lineage, legal basis, and purpose limitation for every processing activity | GDPR Art. 30; EU AI Act Art. 10 |
| 2 | **Data Localization & Cross-Border Mapping** | Authorisation and legal mechanisms for every cross-border data transfer | GDPR Arts. 44–49; DPDP Sec. 16 |
| 3 | **Consent Lifecycle & Individual Rights** | Consent state-machine validity, withdrawal friction, and DSAR erasure-latency SLA (≤ 30 days) | GDPR Arts. 15–17; DPDP Secs. 5, 6, 10–14 |
| 4 | **Technical Controls & Security Posture** | AES-256 at rest, TLS 1.3 in transit, breach-detection automation, and signed DPAs for all processors | GDPR Arts. 25, 28, 33; ISO/IEC 42001 Clause 9 |

---

## 🚀 Running the Functional Prototype

The repository includes a functional Dockerized prototype of the EthosMCP server, demonstrating the core audit capabilities.

### Prerequisites
*   Docker Engine & Docker Compose
*   Git

### Quick Start

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/nyayoshbharuchanb15-max/EthosMCP.git
    cd EthosMCP
    ```

2.  **Configure Environment:**
    Copy `.env.example` to `.env` and set a strong `CRYPTO_KEY`:
    ```bash
    cp .env.example .env
    ```

3.  **Deploy with Docker:**
    ```bash
    docker-compose up --build -d
    ```
    > The server starts without a database. To include the roadmap PostgreSQL service, use:
    > `docker-compose --profile database up --build -d`

4.  **Execute an Audit Vector:**
    ```bash
    # Invoke a single tool via the REST API
    curl -X POST http://localhost:8000/tools/invoke/analyze_data_flow

    # Run the deterministic four-phase workflow end-to-end
    curl -X POST http://localhost:8000/audit/workflow

    # List all registered MCP tools
    curl http://localhost:8000/tools/list
    ```

For full deployment instructions, see [docs/deployment.md](./docs/deployment.md).

---

## 🤖 Connecting an AI Client (Claude Desktop / Cursor)

EthosMCP is a native MCP server. Any MCP-compatible AI client can connect to it directly via `stdio` — no port or API key required. This is the primary integration mode.

1.  **Copy the example config** from [`examples/claude_desktop_config.json`](./examples/claude_desktop_config.json) into your Claude Desktop configuration file:
    *   macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
    *   Windows: `%APPDATA%\Claude\claude_desktop_config.json`

2.  **Update the `cwd` path** to your local clone directory.

3.  **Restart Claude Desktop.** EthosMCP will appear in the MCP server list. You can then ask Claude to run tools such as `audit_ropa_alignment` or `simulate_dsar_workflow` directly in natural language.

For HTTP-based MCP clients, the server exposes a Streamable-HTTP MCP endpoint at `/mcp` when started with `--transport http`.

---

## 🗺️ Architectural Intent vs. Production Roadmap

This repository represents **Phase 0** of a multi-phase delivery. The table below distinguishes what is implemented today from the planned production extensions.

| Layer | Phase 0 (this repository) | Phase 1 Roadmap |
| :--- | :--- | :--- |
| **Data access** | JSON metadata fixtures in `data/` | Live adapters via `asyncpg` (PostgreSQL) and `motor` (MongoDB) |
| **Cryptography** | HMAC-SHA256 + SHA-256 via Python stdlib | RFC 3161 trusted timestamping; X.509 certificate signing |
| **Authentication** | OAuth 2.0 metadata endpoint (`/.well-known/`) | Full JWT proof-of-possession via `python-jose` |
| **Storage** | In-process only | Audit-trail archival to S3 / GCS / Azure Blob |
| **Transport** | `stdio` (AI clients) + REST HTTP | MCP Streamable-HTTP at `/mcp` (already mounted in HTTP mode) |

Install optional dependency groups as each phase is built out:
```bash
pip install "ethosmcp[database]"   # PostgreSQL + MongoDB adapters
pip install "ethosmcp[storage]"    # Cloud storage adapters
pip install "ethosmcp[crypto]"     # RFC 3161 + JWT + X.509
pip install "ethosmcp[all]"        # Everything above
```

---

## 🤝 Governance & Maintenance

*   **Specification Version:** 1.1.0
*   **Maintenance Cycle:** Quarterly reviews to align with emerging regulatory guidance from the EU AI Office and regional Data Protection Authorities.
*   **License:** MIT License. Provided as-is for organizational compliance use.

*Ethical AI is not about filtering outputs. It is about proving the data pipeline is honest from the moment of collection through the moment of deletion.*
