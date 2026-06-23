# EthosMCP Architecture

This document details the architectural design of the EthosMCP server, focusing on its components, interactions, and underlying principles.

## 1. Overview

EthosMCP is built as a modular Model Context Protocol (MCP) server, designed to provide a vendor-neutral framework for AI ethics and data protection compliance audits. It leverages a Python-based stack for its robustness and extensive ecosystem for AI and data governance.

## 2. Core Components

### 2.1. FastMCP Application

The core of the server is built using `fastmcp`, which provides the necessary infrastructure for defining and exposing MCP services. It handles request routing, serialization, and deserialization of MCP messages.

### 2.2. Services Layer

The application logic is organized into distinct services, each corresponding to a phase of the audit workflow:

*   **`governance.py`**: Responsible for auditing Records of Processing Activities (ROPA) and verifying legal bases and purpose limitation as per GDPR and DPDP Act.
*   **`localization.py`**: Focuses on data residency and cross-border data transfer compliance, ensuring data remains within sovereign boundaries.
*   **`sovereignty.py`**: Manages consent lifecycle audits and simulates Data Subject Access Request (DSAR) fulfillment to ensure individual rights are upheld.
*   **`security.py`**: Verifies technical and organizational security measures, including encryption, access controls, and data processing agreements.

### 2.2.1. Workflow Runtime Layer

The live server wiring uses a small orchestration layer:

*   **`workflow/context_engine.py`**: Builds per-request, zero-trust execution context metadata.
*   **`workflow/prompt_manager.py`**: Resolves system and user audit prompts from `src/prompts/`.
*   **`workflow/tool_registry.py`**: Registers MCP tools and routes invocation to service handlers.
*   **`workflow/resource_orchestrator.py`**: Coordinates context + prompts + tool execution for the server API.

### 2.2.2. Prompt and Tool Asset Layers

*   **`src/prompts/`** contains reusable user prompts, system templates, and audit-phase context definitions.
*   **`src/tools/`** provides read-only metadata resource accessors, external adapter placeholders, and knowledge-graph connector placeholders.

### 2.3. Schemas Layer

Pydantic models are used to define the structure and validation rules for all data exchanged within the system, including audit parameters, compliance vectors, and audit reports. This ensures strict type safety and adherence to regulatory requirements.

*   **`gdpr_audit.py`**: Contains Pydantic models for GDPR-specific audit checks.
*   **`dpdp_parameters.py`**: Contains Pydantic models for DPDP Act-specific audit checks.
*   **`eu_ai_act.py`**: Contains Pydantic models for EU AI Act-specific audit checks.

### 2.4. Utilities Layer

This layer provides common utility functions, suchs as cryptographic operations for signing audit reports and hashing data states.

*   **`crypto.py`**: Implements HMAC-SHA256 for response signatures and SHA256 for data state hashing.

## 3. Data Flow

1.  An auditor initiates an MCP request, specifying the audit scope and parameters.
2.  The `fastmcp` application routes the request to the appropriate service (e.g., `governance`, `localization`).
3.  The service retrieves necessary metadata from read-only data sources (e.g., ROPA registries, data flow maps).
4.  Audit checks are performed against the relevant compliance schemas (e.g., GDPR, DPDP, EU AI Act).
5.  An `AuditReport` is generated, containing `AuditResult` instances for each check.
6.  The `AuditReport` is cryptographically signed and hashed using utilities from `crypto.py`.
7.  The signed `AuditReport` is returned to the auditor, providing an immutable and verifiable record of the audit.

## 4. Deployment

EthosMCP is designed for containerized deployment using Docker and Docker Compose, ensuring portability and ease of setup. The `Dockerfile` defines the build process, and `docker-compose.yml` orchestrates the server and its dependencies (e.g., PostgreSQL for audit logs).

For local execution, run:

```bash
python -m src.cli serve --transport stdio
python -m src.cli serve --transport http --port 8000
```

## 5. Security and Compliance Principles

*   **Privacy by Design:** All data processing is designed with privacy in mind, minimizing data exposure and maximizing protection.
*   **Zero-Trust Architecture:** The system operates on the principle that no entity, inside or outside the network perimeter, should be trusted by default. All interactions are authenticated and authorized.
*   **Immutable Audit Trails:** Cryptographic signatures and append-only audit logs ensure the integrity and non-repudiation of all audit results.
*   **Read-Only Access:** The MCP server only performs read operations on organizational data, never modifying or storing sensitive information.
