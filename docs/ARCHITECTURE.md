# AI Governance MCP Server: Technical Architecture

## 1. System Overview and Design Philosophy

The AI Governance MCP Server is a robust, regulation-aware framework designed to provide a comprehensive, auditable, and verifiable governance layer for AI systems. Built upon the Model Context Protocol (MCP), it orchestrates a 9-phase audit pipeline, ensuring compliance with stringent regulatory mandates such as the EU AI Act, GDPR, NIST AI RMF, and ISO 42001. The core philosophy emphasizes **explainability**, **immutability of evidence**, and **machine-readable verifiable credentials** to bridge the gap between high-level regulatory requirements and production-grade AI engineering.

The system is designed for **on-premise native deployment** with a strong focus on **zero-data-egress** in its default configuration, making it suitable for high-value enterprise segments with strict data sovereignty and security requirements. All audit findings are accompanied by plain-language explanations and precise regulatory citations, ensuring transparency and accountability for diverse stakeholders, from senior engineers to compliance officers and data protection authorities.

## 2. Component Interaction Diagram

```mermaid
graph TD
    A[User / AI Assistant] -->|Audit Request| B(MCP Server - TypeScript)
    B -->|API Calls| C(FastAPI Backend - Python)

    subgraph Audit Pipeline (9 Phases)
        C --> P1(1. classify_ai_risk)
        C --> P2(2. audit_supply_chain)
        C --> P3(3. verify_human_oversight)
        C --> P4(4. run_bias_assessment)
        C --> P5(5. generate_dpia)
        C --> P6(6. run_adversarial_tests)
        C --> P7(7. score_audit_weighted)
        C --> P8(8. generate_audit_certificate)
        C --> P9(9. monitor_model_drift)
    end

    P1 -- Blocking Logic --> Blocker[Blocker Middleware]
    P3 -- Blocking Logic --> Blocker
    P7 -- Blocking Logic --> Blocker
    Blocker --|Halt Pipeline / FailNotice| B

    C --> D[Evidence Store - Postgres + JSONB]
    P2 --> E[Provenance Graph - Neo4j]
    P4 --> F[Bias Engine - Fairlearn + AIF360]
    P8 --> G[Certificate Store - W3C VC 2.0]
    P9 --> H[Drift Detection - Evidently AI]

    C -- Webhook Events --> I[Webhook Engine - NATS / Redis Streams]
    I -- Reaudit Trigger --> P9
    G -- Reaudit Pattern --> I

    D -- Immutable Records --> J[Audit Log]
    G -- Cryptographically Signed --> K[Verifiable Credentials]

    B -- Health Check --> L[Monitoring]
    C -- Health Check --> L
```

## 3. Data Flow from Audit Request to Certificate Issuance

1.  **Audit Request Initiation:** A user or AI Assistant (MCP-Compatible) sends an audit request to the **MCP Server (TypeScript)**. This request specifies the AI system to be audited and any relevant parameters.
2.  **MCP Server Orchestration:** The MCP Server acts as the primary interface, registering all 9 audit tools. It handles initial request validation, logging, and connects to the **FastAPI Backend (Python)** for core audit logic execution.
3.  **Phase Execution:** The FastAPI Backend orchestrates the 9-phase audit pipeline sequentially. Each phase corresponds to a specific microservice or function:
    *   **Phase 1 (`classify_ai_risk`):** Classifies the AI system's risk tier (PROHIBITED/HIGH/LIMITED/MINIMAL) based on EU AI Act criteria. The result, `RiskTierResult`, can trigger a `BLOCKER_FAIL`.
    *   **Phase 2 (`audit_supply_chain`):** Scans model provenance, data lineage, third-party components, and IP clearance, storing findings in the **Provenance Graph (Neo4j)** and generating a `ProvenanceReport`.
    *   **Phase 3 (`verify_human_oversight`):** Tests for human-in-the-loop mechanisms, kill-switches, and override capabilities as per EU AI Act Art. 14. A failure here results in an `OversightCertificate` or `BLOCKER_FAIL`.
    *   **Phase 4 (`run_bias_assessment`):** Performs a multidimensional bias scan across protected classes using the **Bias Engine (Fairlearn + AIF360)**, producing a `BiasReport`.
    *   **Phase 5 (`generate_dpia`):** Generates a GDPR Art. 35 DPIA, checking cross-border transfer mechanisms and logging jurisdictional conflicts in a `DPIAReport`.
    *   **Phase 6 (`run_adversarial_tests`):** Executes a robustness suite including prompt injection, OOD, FMEA, and calibration testing, resulting in an `AdversarialReport`.
    *   **Phase 7 (`score_audit_weighted`):** A risk-weighted scoring engine aggregates results from previous phases into a `WeightedAuditScore` framework. This phase can also emit a `BLOCKER_FAIL`.
    *   **Phase 8 (`generate_audit_certificate`):** If no `BLOCKER_FAIL` has occurred, this phase issues a signed audit certificate conforming to W3C Verifiable Credentials 2.0 standards. The certificate (VC-JSON and PDF) is stored in the **Certificate Store**.
    *   **Phase 9 (`monitor_model_drift`):** Continuously monitors for model drift using **Drift Detection (Evidently AI)**, triggering a `DriftAlert` and potentially a reaudit.
4.  **Evidence Storage:** Throughout the pipeline, all phase results, explanations, and regulatory bases are stored immutably in the **Evidence Store (Postgres + JSONB)**. This store is designed for INSERT-only access for audit records, with database-managed timestamps and content hashes to ensure non-repudiation.
5.  **Blocker Logic:** A critical middleware layer in the MCP server's tool chain enforces `BLOCKER_FAIL` conditions from Phases 1, 3, and 7. If a `BLOCKER_FAIL` is detected, the pipeline halts immediately, a `FailNotice` is generated, and no certificate is issued.
6.  **Verifiable Credentials:** The final audit certificate (Phase 8) is a machine-readable, cryptographically signed W3C Verifiable Credential 2.0, with the PDF representation generated directly from the VC-JSON as the source of truth.
7.  **Reaudit Triggers:** The **Webhook Engine (NATS/Redis Streams)** facilitates communication for reaudit patterns. `DriftAlerts` from Phase 9 can trigger new audit requests, closing the loop on continuous governance.

## 4. Technology Selection Rationale

*   **TypeScript for MCP Server:** TypeScript provides strong typing and excellent developer experience for building the MCP server's API layer and tool definitions. Its ecosystem is well-suited for managing communication with external AI assistants and handling diverse transport mechanisms (stdio, SSE).

*   **Python FastAPI for Backend:** FastAPI is chosen for its high performance, asynchronous capabilities, and automatic Pydantic model validation, which is crucial for ensuring data integrity across the microservices. Python's rich ecosystem for AI/ML (Fairlearn, AIF360, Evidently AI) makes it the natural choice for implementing the core audit logic.

*   **Neo4j for Provenance Graph:** A graph database like Neo4j is ideal for representing complex relationships inherent in model provenance, data lineage, and third-party component dependencies. Its native graph query language (Cypher) allows for efficient tracing and IP risk scoring, which would be significantly more cumbersome in a relational database.

*   **Fairlearn + AIF360 for Bias Engine:** Instead of a single library, combining Fairlearn and AIF360 provides a comprehensive toolkit for multidimensional bias assessment. Fairlearn offers mitigation algorithms and fairness metrics, while AIF360 provides a broad range of fairness metrics and bias detection algorithms, allowing for a more thorough and intersectional analysis of protected classes.

*   **NATS / Redis Streams for Webhook Engine:** For this scale, NATS or Redis Streams are preferred over Kafka due to their lightweight nature, ease of deployment, and suitability for event-driven architectures where low-latency message delivery and simple publish/subscribe patterns are paramount. Kafka might be overkill for the initial webhook requirements of reaudit triggers and internal event communication.

*   **Postgres + JSONB for Evidence Store:** PostgreSQL offers robust relational database features combined with native JSONB support. This allows for structured storage of audit session metadata while providing flexible, schema-less storage for the diverse and evolving `result_json` payloads from each audit phase. Its strong transactional guarantees and extensibility make it a reliable choice for an immutable evidence store.

## 5. Failure Modes and Handling

| Failure Mode | Detection Mechanism | Handling Strategy |
|---|---|---|
| **Tool Execution Failure** | Exception handling within FastAPI services; detailed logging. | Return specific error codes and messages; log full stack trace to Evidence Store; potentially trigger a `FailNotice` if critical. |
| **BLOCKER_FAIL Condition** | Middleware in MCP server's tool chain checks for `BLOCKER_FAIL` flags from Phases 1, 3, 7. | Immediately halt pipeline execution; generate `FailNotice`; record halt event in Evidence Store; prevent certificate issuance. |
| **Database Connection Loss** | Connection pooling and retry mechanisms in services. | Implement exponential backoff for retries; alert monitoring system; gracefully degrade or halt if persistent. |
| **External API Unavailability** | Timeout mechanisms and circuit breakers for external calls. | If `ENABLE_LIVE_REGULATORY_FEEDS` is false, use cached data; otherwise, log error, retry, and alert. |
| **Model Drift** | Phase 9 (`monitor_model_drift`) using Evidently AI. | Trigger `DriftAlert` webhook event; initiate a reaudit process; notify relevant stakeholders. |
| **Data Corruption (Evidence Store)** | SHA-256 content hash on `phase_results` table; database triggers reject UPDATE/DELETE. | Hash mismatch alerts; data recovery from backups; forensic analysis of integrity breach. |

## 6. Security Model

*   **Authentication & Authorization:** The MCP Server and FastAPI backend will implement robust authentication mechanisms (e.g., OAuth2/JWT) for external access. Internal service-to-service communication will rely on network-level isolation and mutual TLS where appropriate.
*   **Data Immutability:** The Evidence Store enforces immutability for audit records through INSERT-only access, database-managed `written_at` timestamps, and SHA-256 content hashing. UPDATE and DELETE operations on `phase_results` are rejected by database triggers.
*   **Cryptographic Signing:** W3C Verifiable Credentials (VC 2.0) are cryptographically signed (e.g., Ed25519Signature2020) to ensure non-repudiation and integrity of audit certificates. The `proof` block within the VC-JSON guarantees the authenticity of the issuer and the integrity of the credential subject.
*   **Zero-Data-Egress (Default):** The `docker-compose.yml` is configured to ensure all services communicate on an internal Docker network only. No service makes outbound network calls in the default configuration, minimizing attack surface and ensuring data sovereignty. External API calls are opt-in via `ENABLE_LIVE_REGULATORY_FEEDS` environment variable.
*   **Secrets Management:** Sensitive information (e.g., database passwords, crypto keys) is managed via environment variables, with `.env.example` providing a template. In production, these should be managed by a secure secrets management system.
*   **Least Privilege:** Each service and component operates with the minimum necessary permissions to perform its function.

## 7. Scalability Notes

*   **Horizontal Scaling:** The MCP Server (TypeScript) and FastAPI Backend (Python) are stateless and can be horizontally scaled by deploying multiple instances behind a load balancer. Individual microservices (e.g., Bias Engine, Drift Detection) can also be scaled independently based on their workload.
*   **Database Scaling:** PostgreSQL can be scaled vertically (larger instance) or horizontally (read replicas, sharding) depending on the read/write patterns and data volume. Neo4j also supports clustering for high availability and read scaling.
*   **Message Queue:** NATS or Redis Streams are highly scalable message brokers capable of handling high throughput for webhook events and internal communication.
*   **Limitations:** The primary limitation for extreme horizontal scaling might be the single instance nature of the graph database (Neo4j) or the evidence store (Postgres) if not properly sharded or clustered for very large datasets. However, for typical AI governance audit volumes, the chosen technologies provide ample scalability.
