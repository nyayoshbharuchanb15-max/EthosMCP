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

1.  **[GOVERNANCE.md](./GOVERNANCE.md):** The strategic mandate detailing ethical design choices, zero-trust data handling policies, and alignment with ISO/IEC 42001.
2.  **[AUDITING_FRAMEWORK.md](./AUDITING_FRAMEWORK.md):** The technical blueprint demonstrating the four-phase deterministic audit methodology, cryptographic verification, and DSAR simulation.
3.  **[docs/architecture.md](./docs/architecture.md):** A deeper dive into the specific Python components, FastMCP integration, and Pydantic schemas.
4.  **[docs/compliance_mapping.md](./docs/compliance_mapping.md):** The explicit mapping of statutory legal provisions to programmatic Python audit vectors.

---

## ⚙️ The Four-Phase Audit Workflow

EthosMCP executes compliance audits through a deterministic, sequential protocol:

*   **Phase 1: Governance & ROPA Alignment** - Verifies comprehensive data lineage and strict purpose limitation against the Record of Processing Activities.
*   **Phase 2: Data Localization & Cross-Border Mapping** - Ensures data movement complies with sovereign geographic restrictions (e.g., EEA boundaries, Indian localization).
*   **Phase 3: Consent Lifecycle & Individual Rights** - Validates user sovereignty through granular consent checks and simulated, timed erasure propagation (DSAR testing).
*   **Phase 4: Technical Controls & Security Posture** - Verifies systemic safeguards, including encryption coverage and automated breach response capabilities.

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
    Create a `.env` file in the root directory:
    ```dotenv
    PORT=8000
    DATABASE_URL="postgresql://user:password@db:5432/ethosmcp_db"
    CRYPTO_KEY="your_strong_random_cryptographic_key_here" 
    ```

3.  **Deploy with Docker:**
    ```bash
    docker-compose up --build -d
    ```

4.  **Execute an Audit Vector (Example: Analyze Data Flow):**
    The server exposes HTTP endpoints representing MCP tool invocations.
    ```bash
    curl -X POST http://localhost:8000/localization/analyze_data_flow
    ```
    Run the deterministic four-phase workflow end-to-end:
    ```bash
    curl -X POST http://localhost:8000/audit/workflow
    ```

For full deployment instructions, see [docs/deployment.md](./docs/deployment.md).

---

## 🤝 Governance & Maintenance

*   **Specification Version:** 1.0.0
*   **Maintenance Cycle:** Quarterly reviews to align with emerging regulatory guidance from the EU AI Office and regional Data Protection Authorities.
*   **License:** MIT License. Provided as-is for organizational compliance use.

*Ethical AI is not about filtering outputs. It is about proving the data pipeline is honest from the moment of collection through the moment of deletion.*
