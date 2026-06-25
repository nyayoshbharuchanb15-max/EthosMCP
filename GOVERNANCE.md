# EthosMCP Community Governance

**Status:** Active  
**Version:** 1.0.0  
**Last Reviewed:** June 2026

---

## 1. Purpose & Scope

This document defines the community governance model for the **EthosMCP** open-source project. It covers how decisions are made, how the project is maintained, how regulatory changes are absorbed into the specification, and how contributors can grow into maintainers.

For the technical policy governing the framework's ethical design principles and data-handling mandates, see [FRAMEWORK_GOVERNANCE.md](./FRAMEWORK_GOVERNANCE.md).

---

## 2. Guiding Philosophy

EthosMCP is a **specification-first** project. Its purpose is to translate abstract legal text into deterministic, auditable engineering artefacts. Governance must therefore be equally rigorous: transparent, documented, and reproducible.

*"A standard that cannot be governed cannot be trusted."*

---

## 3. Steering Committee Structure

EthosMCP is governed by a **Dual-Track Steering Committee (DTSC)** composed of two parallel, co-equal tracks. Both tracks must ratify any change that crosses their respective domain boundary.

### 3.1 Track A — Legal & Regulatory (L/R Track)

**Mandate:** Maintain the accuracy, completeness, and currency of the compliance specification — the authoritative mapping between statutory provisions and EthosMCP audit vectors.

**Responsibilities:**
- Monitor legislative and regulatory developments (EU AI Act, GDPR, India's DPDP Act, ISO/IEC 42001, and emerging frameworks).
- Propose and ratify new or amended compliance vectors in response to regulatory changes.
- Review and approve all changes to [docs/compliance_mapping.md](./docs/compliance_mapping.md) and [AUDITING_FRAMEWORK.md](./AUDITING_FRAMEWORK.md).
- Provide legal review commentary on pull requests that touch compliance logic.
- Publish plain-language regulatory change summaries as GitHub Discussions.

**Composition:** 2–5 members with demonstrated expertise in at least one of: data-protection law, AI regulation, information-security law, or international standards compliance.

### 3.2 Track B — Technical Implementation (Tech Track)

**Mandate:** Maintain the quality, security, and architectural integrity of the EthosMCP codebase and its reference implementation.

**Responsibilities:**
- Review and merge pull requests that touch source code, schemas, and infrastructure configuration.
- Maintain the Phase 1 Roadmap (PostgreSQL adapter, OpenAPI schema formalisation).
- Enforce architectural constraints (zero-trust, read-only, metadata-only) at the code level.
- Manage CI/CD pipelines, releases, and the Docker reference image.
- Ensure every new audit vector specified by the L/R Track is technically feasible and has a corresponding implementation issue opened.

**Composition:** 2–5 members with demonstrated expertise in at least one of: Python/FastAPI/MCP development, database engineering, cryptography, or API design.

---

## 4. Decision-Making Process

### 4.1 Standard Decisions (within a single track)

Decisions affecting only one track (e.g., a code refactor or a minor regulatory clarification) follow a **lazy consensus** model:

1. A Steering Committee member opens a GitHub Issue or Pull Request and labels it `governance: track-a` or `governance: track-b`.
2. A **7-day review window** is opened.
3. If no objections are raised within 7 days, the change is considered approved.
4. Any single objection from a track member upgrades the decision to a formal vote.

### 4.2 Cross-Track Decisions (affecting both tracks)

Changes that span both domains (e.g., a new regulatory regime requiring new audit tools, or a breaking API change) require **dual-track ratification**:

1. The proposer opens a GitHub Issue labelled `governance: cross-track` and `RFC`.
2. A **14-day comment period** is opened. All community members may comment.
3. Each track holds an internal vote among its members (simple majority required).
4. The change is approved only when **both tracks vote in favour**.
5. The outcome is documented in the issue and a summary is posted to [Insert link to GitHub Discussions].

### 4.3 Emergency Decisions

In the event of a critical security vulnerability or a time-sensitive regulatory mandate (e.g., a supervisory authority's binding decision with a 30-day compliance window), the DTSC may invoke an **Emergency Fast-Track**:

1. Any Steering Committee member may flag an issue as `priority: emergency`.
2. A 48-hour review window replaces the standard timeline.
3. Approval requires a simple majority across *both* tracks combined.
4. Emergency decisions are subject to a post-hoc review within 30 days.

---

## 5. Regulatory Update Protocol

Regulatory law changes continuously. The following protocol ensures the EthosMCP specification tracks real-world legal evolution without becoming stale.

### 5.1 Trigger Events

A **Regulatory Trigger Event (RTE)** is declared when any of the following occurs:

| Trigger | Examples |
| :--- | :--- |
| Legislative amendment | GDPR recital update, DPDP Act subordinate rules notified |
| Supervisory authority guidance | EDPB opinion, India DPA enforcement notice |
| Court ruling | CJEU judgment affecting data transfer mechanisms |
| New international standard | ISO/IEC 42001 amendment, NIST AI RMF update |
| New jurisdiction added | A contributor proposes adding a new national regime |

### 5.2 Response Workflow

```
RTE Identified
    │
    ▼
L/R Track member opens GitHub Issue: [REGULATORY UPDATE] <title>
Labels: regulatory-update, track-a
    │
    ▼
Legal impact assessment drafted (L/R Track, ≤ 14 days)
    │
    ▼
Affected audit vectors identified & labelled: needs-spec-update
    │
    ▼
Tech Track assesses implementation feasibility (≤ 7 days)
    │
    ▼
Cross-track RFC opened (if new vectors required)
    │
    ▼
Spec updated → Implementation issue(s) opened → PR merged
    │
    ▼
Changelog entry + Governance Discussion posted
```

### 5.3 Deprecation of Superseded Provisions

When a statutory provision is repealed or substantively amended, the corresponding audit vector is first marked `status: under-review` and then either updated or deprecated via the standard cross-track process. Deprecated vectors are retained in the specification history but excluded from active audits.

---

## 6. Roles & Contribution Ladder

| Role | Description | Path to Advancement |
| :--- | :--- | :--- |
| **Community Member** | Anyone who opens an issue, comments, or submits a PR | No formal requirement |
| **Contributor** | Has had ≥ 1 pull request merged | Automatic on first merged PR |
| **Recurring Contributor** | Has had ≥ 5 pull requests merged across ≥ 3 months | Automatic; gains triage rights on issues |
| **Maintainer (Track)** | Trusted contributor invited to join one track of the DTSC | Nominated by existing Steering member; ratified by simple majority of that track |
| **Steering Member** | Full DTSC member with ratification rights | Promotion from Maintainer; requires approval from both tracks |

### 6.1 Becoming a Maintainer

If you are a Recurring Contributor and are interested in joining the Steering Committee:

1. Express your interest by opening a GitHub Discussion titled `[Maintainer Nomination] Your Name — Track A/B`.
2. Describe your relevant expertise and your three most impactful contributions to the project.
3. An existing Steering Committee member must second your nomination within 14 days.
4. The relevant track votes (7-day window; simple majority of current track members).
5. If approved, you are added to the [CODEOWNERS](./.github/CODEOWNERS) file and the Steering Committee roster below.

---

## 7. Current Steering Committee

| Name | Track | GitHub | Expertise |
| :--- | :--- | :--- | :--- |
| Nyayosh Bharucha | Founder / L/R Track Lead | [@nyayoshbharuchanb15-max](https://github.com/nyayoshbharuchanb15-max) | AI Governance, GDPR, DPDP, EU AI Act |
| *(Seeking members)* | Tech Track Lead | — | Python, FastAPI, MCP, Database Engineering |
| *(Seeking members)* | L/R Track | — | Data-Protection Law, ISO 42001 |

> **We are actively recruiting founding Steering Committee members.** If you have relevant expertise and a sustained interest in AI governance tooling, please see [CONTRIBUTING.md](./CONTRIBUTING.md) and open a nomination discussion.

---

## 8. Repository Administration

- **Issue Triage:** Recurring Contributors and above may apply labels and close stale issues.
- **Merging PRs:** Requires approval from ≥ 1 Steering Member of the relevant track. Cross-track PRs require approval from both tracks.
- **Releases:** Proposed by the Tech Track; must include a Changelog that the L/R Track reviews for regulatory accuracy.
- **Forking & Licensing:** Governed by the [MIT License](./LICENSE). Forks are encouraged; attribution is required.

---

## 9. Amendments to This Document

This governance document is itself subject to the cross-track decision process (Section 4.2). Proposed amendments must be submitted as pull requests against this file, labelled `governance: meta`.

---

## 10. Contact

For governance questions, open a GitHub Discussion in the [Governance category](https://github.com/nyayoshbharuchanb15-max/EthosMCP/discussions).  
For security concerns, see [SECURITY.md](./SECURITY.md).
