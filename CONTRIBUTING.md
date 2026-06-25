# Contributing to EthosMCP

Thank you for your interest in EthosMCP — a specification-driven, zero-trust compliance architecture for operationalising AI governance law into deterministic, auditable engineering workflows.

This project sits at the intersection of **legal scholarship** and **software engineering**. Both perspectives are essential, and we welcome contributors from either discipline — or both. You do not need to be a software engineer to make a meaningful contribution.

---

## Table of Contents

1. [Who We Are Looking For](#1-who-we-are-looking-for)
2. [Current Priority: Phase 1 MVP](#2-current-priority-phase-1-mvp)
3. [How to Get Involved](#3-how-to-get-involved)
   - [For Non-Coders (Legal & Compliance Experts)](#for-non-coders-legal--compliance-experts)
   - [For Engineers & Technical Contributors](#for-engineers--technical-contributors)
4. [Contribution Types](#4-contribution-types)
5. [Proposing a New Audit Vector or Regulatory Mapping](#5-proposing-a-new-audit-vector-or-regulatory-mapping)
6. [Development Workflow (Engineers)](#6-development-workflow-engineers)
7. [Coding Standards](#7-coding-standards)
8. [Pull Request Guidelines](#8-pull-request-guidelines)
9. [Issue Labels Reference](#9-issue-labels-reference)
10. [Communication Channels](#10-communication-channels)
11. [Recognition](#11-recognition)

---

## 1. Who We Are Looking For

EthosMCP is an **architect-led** open-source project. The framework was designed by a legal and regulatory domain expert. We are now seeking contributors to bring the full vision to life.

We are actively looking for people with expertise in:

**Legal & Compliance**
- GDPR, EU AI Act, India's Digital Personal Data Protection (DPDP) Act
- ISO/IEC 42001 (AI Management Systems)
- Information security law, data-transfer mechanisms (SCCs, BCRs)
- Regulatory impact assessment, DPIA, or ROPA experience

**Engineering & Technical**
- **Python** (FastAPI, Pydantic, `asyncpg`, `motor`) — *highest priority*
- **Database Engineering** (PostgreSQL schema design, query optimisation)
- **OpenAPI / JSON Schema** formalisation
- **Cryptography** (HMAC, SHA-256, RFC 3161 timestamping, X.509)
- **Docker / container infrastructure**
- **MCP (Model Context Protocol)** server development
- **Technical writing** for developer documentation

---

## 2. Current Priority: Phase 1 MVP

The repository currently contains a **Phase 0 functional prototype** backed by JSON fixtures. The immediate community goal is to build the **Phase 1 Reference Implementation**, which replaces the fixtures with real, live data adapters.

### 🎯 What We Need Engineers to Build

| Priority | Task | Skills Required | Issue Label |
| :---: | :--- | :--- | :--- |
| 🔴 Critical | **PostgreSQL toy-database adapter** — a self-contained Docker Compose service with a seed schema representing a fictional company's ROPA, consent, and data-flow records | Python (`asyncpg`), PostgreSQL, Docker | [`phase1-database`](https://github.com/nyayoshbharuchanb15-max/EthosMCP/labels/phase1-database) |
| 🔴 Critical | **Formalise OpenAPI 3.1 schemas** — convert the existing Pydantic models into a machine-readable, versioned OpenAPI specification file | OpenAPI, JSON Schema, Python | [`phase1-openapi`](https://github.com/nyayoshbharuchanb15-max/EthosMCP/labels/phase1-openapi) |
| 🟠 High | **Live `asyncpg` data-source adapter** replacing JSON fixture reads | Python, asyncpg | [`phase1-database`](https://github.com/nyayoshbharuchanb15-max/EthosMCP/labels/phase1-database) |
| 🟠 High | **DSAR simulation against PostgreSQL** — verify erasure propagation through the seed database within latency SLAs | Python, SQL | [`phase1-dsar`](https://github.com/nyayoshbharuchanb15-max/EthosMCP/labels/phase1-dsar) |
| 🟡 Medium | **CI pipeline** (GitHub Actions) — lint, test, and build the Docker image on every PR | GitHub Actions, Docker | [`ci-cd`](https://github.com/nyayoshbharuchanb15-max/EthosMCP/labels/ci-cd) |
| 🟡 Medium | **Integration test suite** for all four audit phases against the seed database | pytest, Docker Compose | [`testing`](https://github.com/nyayoshbharuchanb15-max/EthosMCP/labels/testing) |

> **New to MCP?** The [Model Context Protocol documentation](https://modelcontextprotocol.io/docs) is the best starting point. The existing `src/` directory is well-commented and is a working reference.

---

## 3. How to Get Involved

### For Non-Coders (Legal & Compliance Experts)

You do not need to write a single line of code to make a high-value contribution to EthosMCP.

**Step 1 — Read the core documents.**
Start with:
- [`README.md`](./README.md) — project overview
- [`AUDITING_FRAMEWORK.md`](./AUDITING_FRAMEWORK.md) — the four-phase audit methodology
- [`docs/compliance_mapping.md`](./docs/compliance_mapping.md) — statutory provisions mapped to audit vectors

**Step 2 — Identify a gap or improvement.**
Ask yourself:
- Is a legal provision incorrectly cited or mischaracterised?
- Is a significant regulation missing (e.g., the UK GDPR, Brazil's LGPD, Canada's PIPEDA)?
- Is an audit vector under-specified or legally incomplete?
- Does the DSAR simulation correctly reflect the ≤ 30-day GDPR erasure SLA?

**Step 3 — Open an Issue.**
Navigate to the [Issue Tracker](https://github.com/nyayoshbharuchanb15-max/EthosMCP/issues) and open a new issue using the **Regulatory Mapping / Audit Vector** template. Describe the legal provision, the gap, and your proposed change. You do not need to write the fix yourself.

**Step 4 — Join the discussion.**
Browse open issues and pull requests. Leave comments, flag legal inaccuracies, or confirm that a proposed vector correctly reflects the law. Your expert review is directly valuable to the engineering contributors implementing the change.

**Step 5 — Consider joining the Steering Committee.**
If you contribute regularly, you are eligible to join the Legal & Regulatory Track of the Dual-Track Steering Committee. See [GOVERNANCE.md](./GOVERNANCE.md) for details.

---

### For Engineers & Technical Contributors

**Step 1 — Set up the development environment.**

```bash
# 1. Fork and clone the repository
git clone https://github.com/<your-username>/EthosMCP.git
cd EthosMCP

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3. Install dependencies (including dev extras)
pip install -r requirements.txt

# 4. Copy environment configuration
cp .env.example .env
# Open .env and set a strong CRYPTO_KEY value

# 5. Verify the test suite passes
python -m pytest -q
```

**Step 2 — Run the prototype.**

```bash
# Option A: Docker (recommended for full-stack development)
docker-compose up --build

# Option B: Direct Python (for rapid iteration on the MCP server)
python -m ethosmcp
```

**Step 3 — Find a task.**
Browse the [Issue Tracker](https://github.com/nyayoshbharuchanb15-max/EthosMCP/issues) and filter by:
- [`good first issue`](https://github.com/nyayoshbharuchanb15-max/EthosMCP/labels/good%20first%20issue) — well-scoped tasks for new contributors
- [`phase1-database`](https://github.com/nyayoshbharuchanb15-max/EthosMCP/labels/phase1-database) — PostgreSQL MVP work
- [`phase1-openapi`](https://github.com/nyayoshbharuchanb15-max/EthosMCP/labels/phase1-openapi) — schema formalisation
- [`help wanted`](https://github.com/nyayoshbharuchanb15-max/EthosMCP/labels/help%20wanted) — tasks where the maintainers specifically need community help

**Step 4 — Comment on the issue** before starting work, so we can avoid duplication and give you any context you need.

**Step 5 — Submit a Pull Request.** Follow the [Development Workflow](#6-development-workflow-engineers) and [Pull Request Guidelines](#8-pull-request-guidelines) below.

---

## 4. Contribution Types

| Type | Examples | Code Required? |
| :--- | :--- | :---: |
| **Regulatory review** | Correct a legal citation, add a missing provision | No |
| **Audit vector proposal** | Propose a new compliance check for a new regulation | No |
| **Compliance mapping** | Map provisions from a new jurisdiction (e.g., UK GDPR, LGPD) | No |
| **Documentation** | Improve README, clarify architecture docs, fix broken links | No |
| **Bug fix** | Fix a failing audit vector, correct a cryptographic signature | Yes |
| **Phase 1 feature** | PostgreSQL adapter, OpenAPI spec, CI pipeline | Yes |
| **Test coverage** | Add pytest tests for existing audit tools | Yes |
| **Security hardening** | Improve cryptographic implementation | Yes |

---

## 5. Proposing a New Audit Vector or Regulatory Mapping

An **audit vector** is a programmatic compliance check that maps to one or more statutory provisions. Adding a new one is one of the highest-value contributions to the project.

### Proposal Process

1. **Open an Issue** using the [Audit Vector Proposal template](https://github.com/nyayoshbharuchanb15-max/EthosMCP/issues/new?template=feature_request.md). Your proposal must include:

   | Field | Description |
   | :--- | :--- |
   | **Regulation / Standard** | Full name and article/section reference (e.g., "GDPR Art. 22 — Automated Decision-Making") |
   | **Jurisdiction** | EU, India, UK, Brazil, etc. |
   | **Obligation** | Plain-language description of what the law requires |
   | **Proposed Vector Name** | A snake_case identifier (e.g., `audit_automated_decision_making`) |
   | **What the vector checks** | What data or metadata the audit tool would inspect |
   | **Pass / Fail criteria** | Exact conditions under which the vector returns `PASS` or `FAIL` |
   | **Statutory latency** | Any time-bound compliance requirement (e.g., "breach notification ≤ 72 hours") |

2. The **L/R Track** will review the legal accuracy of the proposal (≤ 14 days).
3. The **Tech Track** will confirm technical feasibility and open an implementation issue.
4. Once both tracks approve, the vector is added to [`docs/compliance_mapping.md`](./docs/compliance_mapping.md) and an engineering issue is created.

---

## 6. Development Workflow (Engineers)

```bash
# 1. Create a feature branch from main
git checkout -b feat/your-feature-name

# 2. Make your changes
# ...

# 3. Run the test suite
python -m pytest -q

# 4. Lint your code
ruff check src/ tests/

# 5. Commit with a conventional commit message
git commit -m "feat(database): add asyncpg adapter for ROPA registry"

# 6. Push and open a Pull Request
git push origin feat/your-feature-name
```

### Conventional Commit Types

| Prefix | Use for |
| :--- | :--- |
| `feat` | New audit vector, new adapter, new API endpoint |
| `fix` | Bug fix in existing functionality |
| `docs` | Documentation changes only |
| `test` | Adding or correcting tests |
| `refactor` | Code restructuring with no functional change |
| `chore` | Build scripts, CI, dependency updates |
| `spec` | Changes to compliance mappings or audit vector specifications |

---

## 7. Coding Standards

- **Python 3.11+** is required. Use type annotations throughout.
- **Pydantic v2** for all data models and validation.
- **Ruff** for linting. Your PR will fail CI if ruff reports errors.
- **pytest** for all tests. Aim for ≥ 80% coverage on new code.
- **Zero raw personal data:** The zero-trust boundary is a hard architectural constraint. No PR may introduce logic that reads, logs, or transmits raw personal data. All new tools must operate on metadata, schemas, or aggregates only.
- **Cryptographic signatures:** All new audit tools that return compliance verdicts must include `state_hash` and `response_signature` fields in their response models, consistent with the existing `AuditResult` schema.

---

## 8. Pull Request Guidelines

Before submitting a PR, please confirm:

- [ ] The test suite passes locally (`python -m pytest -q`).
- [ ] `ruff check src/ tests/` returns no errors.
- [ ] The PR description references the relevant issue number (`Closes #<issue>`).
- [ ] Changes to compliance logic include a reference to the statutory provision being implemented.
- [ ] No secrets, credentials, or personal data are included in the changeset.
- [ ] If you added a new dependency, it is added to both `requirements.txt` and `pyproject.toml`.

PRs will be reviewed by at least one member of the relevant Steering Committee track. Please allow up to **7 business days** for a first review on non-emergency contributions. We will always acknowledge receipt within 48 hours.

---

## 9. Issue Labels Reference

| Label | Meaning |
| :--- | :--- |
| `good first issue` | Suitable for new contributors; well-scoped |
| `help wanted` | Maintainers are actively seeking community help |
| `phase1-database` | PostgreSQL MVP implementation work |
| `phase1-openapi` | OpenAPI / JSON Schema formalisation |
| `phase1-dsar` | DSAR simulation against live database |
| `regulatory-update` | A real-world legal change requires a spec update |
| `audit-vector-proposal` | Proposal for a new compliance check |
| `legal-review-needed` | Requires review by the L/R Track before merging |
| `governance: cross-track` | Requires approval from both Steering Committee tracks |
| `security` | Security-sensitive change — handled with extra care |
| `bug` | Something is not working as specified |
| `documentation` | Documentation-only change |

---

## 10. Communication Channels

| Channel | Purpose |
| :--- | :--- |
| [GitHub Issues](https://github.com/nyayoshbharuchanb15-max/EthosMCP/issues) | Bug reports, feature proposals, audit vector proposals |
| [GitHub Discussions](https://github.com/nyayoshbharuchanb15-max/EthosMCP/discussions) | General questions, regulatory news, architecture discussions |
| Pull Request comments | In-line technical review |

We do not use external chat platforms. All significant decisions are documented publicly in GitHub, ensuring the project's governance history is transparent and auditable.

---

## 11. Recognition

Every contributor is recognised in the project. When your first PR is merged, you will be added to the project's contributor acknowledgements. Sustained contributors are eligible to join the Steering Committee and become maintainers (see [GOVERNANCE.md](./GOVERNANCE.md)).

---

*EthosMCP is MIT-licensed. By contributing, you agree that your contributions will be licensed under the same terms.*

*Thank you for helping make AI governance auditable.*
