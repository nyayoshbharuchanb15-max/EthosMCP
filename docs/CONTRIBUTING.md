# Contributing to AI Governance MCP Server

We welcome contributions to the AI Governance MCP Server! Whether you are a developer, a legal expert, or a compliance officer, your input helps make this framework more robust and effective.

## Code of Conduct
Please be respectful and professional in all interactions. We aim to build a collaborative community focused on ethical AI governance.

## Development Standards

### TypeScript (MCP Server)
- Use functional programming patterns where possible.
- All new tools must include Zod schema validation.
- Every tool MUST return an `explanation` field with regulatory citations.
- Run `npm run lint` and `npm test` before submitting PRs.

### Python (API & Services)
- Use FastAPI and Pydantic for all new endpoints.
- Follow PEP 8 guidelines.
- Use type hints for all function signatures.
- Document every regulatory check with its specific article number (e.g., `EU AI Act Art. 14`).

### Documentation
- Use Mermaid for all architectural and data flow diagrams.
- Keep the `REGULATORY_MAPPING.md` updated with any new provisions covered by the code.
- Write explanations in plain language suitable for non-technical stakeholders.

## Submission Process
1. Fork the repository.
2. Create a feature branch (`git checkout -b feat/your-feature`).
3. Commit your changes using conventional commits (e.g., `feat: add NIST AI RMF mapping for phase 4`).
4. Push to your branch and open a Pull Request.

## Regulatory Accuracy
If you find an error in a regulatory citation or mapping, please open an issue immediately with the label `regulatory-fix`. Accuracy is our highest priority.
