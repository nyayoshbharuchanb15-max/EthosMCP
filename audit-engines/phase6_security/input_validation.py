from __future__ import annotations

import json
import re
from typing import Any

from pydantic import BaseModel, Field


class ValidationFinding(BaseModel):
    check: str
    passed: bool
    severity: str
    category: str
    detail: str
    recommendation: str | None = None


class InputValidationResult(BaseModel):
    findings: list[ValidationFinding] = Field(default_factory=list)
    overall_pass: bool = False
    total_checks: int = 0
    passed_checks: int = 0


OWASP_LLM_TOP_10_CHECKS: list[dict[str, Any]] = [
    {
        "id": "LLM01",
        "title": "Prompt Injection",
        "description": "Check for prompt injection attack patterns in input",
        "severity": "CRITICAL",
    },
    {
        "id": "LLM02",
        "title": "Insecure Output Handling",
        "description": "Check for insecure handling of LLM-generated output",
        "severity": "HIGH",
    },
    {
        "id": "LLM03",
        "title": "Training Data Poisoning",
        "description": "Check for potential training data poisoning vectors in input",
        "severity": "HIGH",
    },
    {
        "id": "LLM04",
        "title": "Model Denial of Service",
        "description": "Check for inputs that could cause excessive resource consumption",
        "severity": "MEDIUM",
    },
    {
        "id": "LLM05",
        "title": "Supply Chain Vulnerabilities",
        "description": "Check input for indicators of supply chain compromise",
        "severity": "HIGH",
    },
    {
        "id": "LLM06",
        "title": "Sensitive Information Disclosure",
        "description": "Check for sensitive information in input that should be filtered",
        "severity": "CRITICAL",
    },
    {
        "id": "LLM07",
        "title": "Insecure Plugin Design",
        "description": "Check for plugin invocation patterns that could be exploited",
        "severity": "MEDIUM",
    },
    {
        "id": "LLM08",
        "title": "Excessive Agency",
        "description": "Check for inputs requesting excessive permissions or actions",
        "severity": "MEDIUM",
    },
    {
        "id": "LLM09",
        "title": "Overreliance",
        "description": "Check for inputs that indicate blind trust in model output",
        "severity": "LOW",
    },
    {
        "id": "LLM10",
        "title": "Model Theft",
        "description": "Check for model extraction attempts in input",
        "severity": "HIGH",
    },
]

PROMPT_INJECTION_PATTERNS: list[re.Pattern] = [
    re.compile(r"ignore\s+(all\s+)?(previous|prior|above)\s+(instructions|prompts|context|directions)", re.IGNORECASE),
    re.compile(r"(system|assistant)\s*(prompt|message|instruction)", re.IGNORECASE),
    re.compile(r"you\s+(are\s+)?now\s+(free|DAN|jailbreak)", re.IGNORECASE),
    re.compile(r"act\s+as\s+(if\s+)?you\s+(are|were)", re.IGNORECASE),
    re.compile(r"bypass\s+(the\s+)?(content|policy|guidelines|restrictions)", re.IGNORECASE),
    re.compile(r"reveal\s+(the\s+)?(system|secret|hidden|internal)", re.IGNORECASE),
    re.compile(r"role[-\s]?play", re.IGNORECASE),
    re.compile(r"do\s+(not\s+)?(have\s+)?(any\s+)?(restrictions|limitations|boundaries)", re.IGNORECASE),
    re.compile(r"output\s+(the\s+)?(raw|original|full|entire)", re.IGNORECASE),
    re.compile(r"pretend\s+(to\s+)?be", re.IGNORECASE),
]

SENSITIVE_DATA_PATTERNS: list[re.Pattern] = [
    re.compile(r"\b\d{16}\b"),
    re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    re.compile(r"(password|secret|api[_-]?key|token|credential)s?\s*[:=]\s*\S+", re.IGNORECASE),
    re.compile(r"(bearer|basic)\s+[A-Za-z0-9\-._~+/]+=*", re.IGNORECASE),
    re.compile(r"\b[A-Za-z0-9+/]{40,}\b"),
]


class InputValidationChecker:
    def validate_schema(
        self,
        input_schema: dict[str, Any],
        actual_input: dict[str, Any],
    ) -> InputValidationResult:
        findings: list[ValidationFinding] = []

        schema_findings = self._check_schema_compliance(input_schema, actual_input)
        findings.extend(schema_findings)

        owasp_findings = self._check_owasp_llm_top_10(actual_input)
        findings.extend(owasp_findings)

        injection_findings = self._check_prompt_injection(actual_input)
        findings.extend(injection_findings)

        passed_count = sum(1 for f in findings if f.passed)
        total_count = len(findings)
        overall_pass = passed_count == total_count if total_count > 0 else True

        return InputValidationResult(
            findings=findings,
            overall_pass=overall_pass,
            total_checks=total_count,
            passed_checks=passed_count,
        )

    def _check_schema_compliance(
        self,
        schema: dict[str, Any],
        actual: dict[str, Any],
    ) -> list[ValidationFinding]:
        findings: list[ValidationFinding] = []
        required_fields = schema.get("required", [])
        properties = schema.get("properties", {})

        for field in required_fields:
            field_present = field in actual
            findings.append(
                ValidationFinding(
                    check=f"required_field_{field}",
                    passed=field_present,
                    severity="BLOCKER" if not field_present else "INFO",
                    category="schema_validation",
                    detail=f"Required field '{field}' is {'present' if field_present else 'missing'} in input",
                    recommendation=f"Ensure '{field}' is provided in the input payload"
                    if not field_present
                    else None,
                )
            )

        for field, value in actual.items():
            expected_type = properties.get(field, {}).get("type")
            if expected_type and value is not None:
                type_ok = self._check_type(value, expected_type)
                findings.append(
                    ValidationFinding(
                        check=f"type_check_{field}",
                        passed=type_ok,
                        severity="WARNING" if not type_ok else "INFO",
                        category="schema_validation",
                        detail=f"Field '{field}' expects type '{expected_type}', "
                        f"got '{type(value).__name__}'",
                        recommendation=f"Convert '{field}' to {expected_type}"
                        if not type_ok
                        else None,
                    )
                )

        return findings

    def _check_type(self, value: Any, expected_type: str) -> bool:
        type_map: dict[str, type] = {
            "string": str,
            "integer": int,
            "number": (int, float),
            "boolean": bool,
            "array": list,
            "object": dict,
        }
        py_type = type_map.get(expected_type)
        if py_type is None:
            return True
        return isinstance(value, py_type)

    def _check_owasp_llm_top_10(
        self, actual_input: dict[str, Any]
    ) -> list[ValidationFinding]:
        findings: list[ValidationFinding] = []
        input_text = json.dumps(actual_input)

        for check in OWASP_LLM_TOP_10_CHECKS:
            passed = True
            detail = f"OWASP {check['id']}: {check['title']} — {check['description']}"

            if check["id"] == "LLM01":
                for pattern in PROMPT_INJECTION_PATTERNS:
                    if pattern.search(input_text):
                        passed = False
                        detail = f"OWASP LLM01: Prompt injection pattern detected matching '{pattern.pattern}'"
                        break
            elif check["id"] == "LLM04":
                deeply_nested = len(input_text) > 50000
                passed = not deeply_nested
                detail = "OWASP LLM04: Input size within acceptable limits" if passed else "OWASP LLM04: Input size exceeds 50KB — potential DoS vector"
            elif check["id"] == "LLM06":
                for pattern in SENSITIVE_DATA_PATTERNS:
                    if pattern.search(input_text):
                        passed = False
                        detail = f"OWASP LLM06: Potential sensitive data pattern detected matching '{pattern.pattern}'"
                        break

            findings.append(
                ValidationFinding(
                    check=f"owasp_{check['id']}",
                    passed=passed,
                    severity=check["severity"] if not passed else "INFO",
                    category="owasp_llm_top_10",
                    detail=detail,
                    recommendation=(
                        f"Address OWASP {check['id']} vulnerability: {check['title']}"
                        if not passed
                        else None
                    ),
                )
            )

        return findings

    def _check_prompt_injection(
        self, actual_input: dict[str, Any]
    ) -> list[ValidationFinding]:
        findings: list[ValidationFinding] = []
        input_text = json.dumps(actual_input)

        detected_patterns: list[str] = []
        for pattern in PROMPT_INJECTION_PATTERNS:
            matches = pattern.findall(input_text)
            if matches:
                detected_patterns.append(pattern.pattern)

        passed = len(detected_patterns) == 0
        findings.append(
            ValidationFinding(
                check="prompt_injection_detection",
                passed=passed,
                severity="CRITICAL" if not passed else "INFO",
                category="prompt_injection",
                detail="No prompt injection patterns detected"
                if passed
                else f"Prompt injection patterns detected: {', '.join(detected_patterns[:5])}",
                recommendation="Sanitize input to remove prompt injection payloads. "
                "Implement input validation and output encoding."
                if not passed
                else None,
            )
        )

        return findings
