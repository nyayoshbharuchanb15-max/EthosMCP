from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class PbDFinding(BaseModel):
    check: str
    passed: bool
    article: str
    detail: str
    recommendation: str | None = None
    severity: str = "INFO"


class PbDChecklistResult(BaseModel):
    findings: list[PbDFinding] = Field(default_factory=list)
    overall_score: float = 0.0
    compliant: bool = False


PBD_CHECKLIST: list[dict[str, str]] = [
    {
        "check": "pseudonymization",
        "article": "Art 25(1)",
        "description": "Pseudonymisation of personal data as soon as the processing purpose permits",
        "recommendation": "Implement pseudonymisation techniques such as hashing, tokenization, or encryption of identifiers.",
    },
    {
        "check": "data_minimization",
        "article": "Art 5(1)(c)",
        "description": "Data collected is adequate, relevant, and limited to what is necessary",
        "recommendation": "Review data fields collected — eliminate any that are not strictly necessary for the stated purpose.",
    },
    {
        "check": "access_controls",
        "article": "Art 25(2)",
        "description": "Access controls ensure only authorised personnel can process personal data",
        "recommendation": "Implement RBAC with least-privilege principle. Enable audit logging of all data access.",
    },
    {
        "check": "retention_policies",
        "article": "Art 5(1)(e)",
        "description": "Data retention periods are defined and enforced",
        "recommendation": "Define retention schedule per data category. Implement automated deletion or anonymisation after retention period.",
    },
    {
        "check": "encryption_at_rest",
        "article": "Art 32(1)(a)",
        "description": "Personal data encrypted at rest using industry-standard algorithms",
        "recommendation": "Use AES-256 encryption for stored personal data. Manage keys via HSM or KMS.",
    },
    {
        "check": "encryption_in_transit",
        "article": "Art 32(1)(a)",
        "description": "Personal data encrypted in transit using TLS 1.2+",
        "recommendation": "Enforce TLS 1.2 minimum. Disable weak cipher suites. Use HSTS where applicable.",
    },
    {
        "check": "transparency",
        "article": "Art 5(1)(a) & Art 13-14",
        "description": "Data subjects informed of processing in a concise, transparent, and intelligible manner",
        "recommendation": "Provide privacy notice at data collection point. Include identity of controller, purposes, legal basis, retention, and rights.",
    },
    {
        "check": "purpose_limitation",
        "article": "Art 5(1)(b)",
        "description": "Data collected for specified, explicit, and legitimate purposes only",
        "recommendation": "Document purpose specification for each processing activity. Prohibit further processing incompatible with original purpose.",
    },
    {
        "check": "data_portability",
        "article": "Art 20",
        "description": "Data subjects can receive their data in a structured, commonly used, machine-readable format",
        "recommendation": "Provide self-service data export in JSON or CSV format. Support direct transmission between controllers.",
    },
    {
        "check": "breach_notification",
        "article": "Art 33-34",
        "description": "Breach detection, notification to supervisory authority (72h), and communication to data subjects",
        "recommendation": "Implement breach detection and response plan. Automate notification workflows.",
    },
]


class PrivacyByDesignChecker:
    def check(self, data_lineage: dict[str, Any]) -> PbDChecklistResult:
        findings: list[PbDFinding] = []
        controls = data_lineage.get("controls", {})
        if not isinstance(controls, dict):
            controls = {}
        passed_count = 0

        for item in PBD_CHECKLIST:
            check_key = item["check"]
            control_value = controls.get(check_key)
            passed = self._evaluate_control(check_key, control_value, data_lineage)
            if passed:
                passed_count += 1
            finding = PbDFinding(
                check=item["check"],
                passed=passed,
                article=item["article"],
                detail=item["description"],
                recommendation=item["recommendation"] if not passed else None,
                severity="INFO" if passed else "WARNING",
            )
            findings.append(finding)

        overall_score = passed_count / len(PBD_CHECKLIST) if PBD_CHECKLIST else 0.0
        compliant = overall_score >= 0.8

        return PbDChecklistResult(
            findings=findings,
            overall_score=round(overall_score, 2),
            compliant=compliant,
        )

    def _evaluate_control(
        self,
        check_key: str,
        control_value: Any,
        data_lineage: dict[str, Any],
    ) -> bool:
        if control_value is not None:
            if isinstance(control_value, bool):
                return control_value
            if isinstance(control_value, dict):
                return control_value.get("enabled", False)
            if isinstance(control_value, str):
                return control_value.lower() in ("true", "yes", "enabled", "implemented")
            return bool(control_value)

        lineage = data_lineage.get("data_lineage", {})
        if not isinstance(lineage, dict):
            return False

        if check_key == "pseudonymization":
            transformations = lineage.get("transformations", [])
            if isinstance(transformations, list):
                return any(
                    isinstance(t, dict) and t.get("type") == "pseudonymize"
                    for t in transformations
                )
            return False

        if check_key == "data_minimization":
            fields = lineage.get("fields", {})
            if isinstance(fields, dict):
                purpose_fields = fields.get("purpose_fields", [])
                collected_fields = fields.get("collected_fields", [])
                return len(collected_fields) <= len(purpose_fields) + 2
            return False

        if check_key == "access_controls":
            roles = lineage.get("roles", [])
            return isinstance(roles, list) and len(roles) > 0

        if check_key == "retention_policies":
            policies = lineage.get("retention_policies", {})
            return isinstance(policies, dict) and len(policies) > 0

        return False
