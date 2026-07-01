from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class DataMinFinding(BaseModel):
    check: str
    passed: bool
    article: str
    detail: str
    recommendation: str | None = None
    severity: str = "INFO"


class DataMinimisationResult(BaseModel):
    findings: list[DataMinFinding] = Field(default_factory=list)
    compliant: bool = False
    overall_score: float = 0.0


class DataMinimisationChecker:
    def check(self, data_lineage: dict[str, Any]) -> DataMinimisationResult:
        findings: list[DataMinFinding] = []

        finding_adequacy = self._check_data_adequacy(data_lineage)
        findings.extend(finding_adequacy)

        finding_relevance = self._check_data_relevance(data_lineage)
        findings.extend(finding_relevance)

        finding_necessity = self._check_data_necessity(data_lineage)
        findings.extend(finding_necessity)

        finding_purpose = self._check_purpose_limitation(data_lineage)
        findings.extend(finding_purpose)

        finding_retention = self._check_retention_periods(data_lineage)
        findings.extend(finding_retention)

        passed_count = sum(1 for f in findings if f.passed)
        overall_score = passed_count / len(findings) if findings else 0.0
        compliant = overall_score >= 0.8

        return DataMinimisationResult(
            findings=findings,
            compliant=compliant,
            overall_score=round(overall_score, 2),
        )

    def _check_data_adequacy(
        self, data_lineage: dict[str, Any]
    ) -> list[DataMinFinding]:
        findings: list[DataMinFinding] = []
        fields = data_lineage.get("fields", {})
        if not isinstance(fields, dict):
            fields = {}

        collected = fields.get("collected_fields", [])
        purpose_fields = fields.get("purpose_fields", [])
        if not isinstance(collected, list):
            collected = []
        if not isinstance(purpose_fields, list):
            purpose_fields = []

        excess = [f for f in collected if f not in purpose_fields]
        findings.append(
            DataMinFinding(
                check="data_adequacy",
                passed=len(excess) == 0,
                article="Art 5(1)(c)",
                detail=f"Collected fields: {len(collected)}, Purpose-required fields: {len(purpose_fields)}. "
                f"Excess fields: {len(excess)}"
                if excess
                else "All collected fields are adequate for stated purposes",
                recommendation=f"Remove or justify excess fields: {', '.join(excess[:10])}"
                if excess
                else None,
                severity="WARNING" if excess else "INFO",
            )
        )

        return findings

    def _check_data_relevance(
        self, data_lineage: dict[str, Any]
    ) -> list[DataMinFinding]:
        findings: list[DataMinFinding] = []
        fields = data_lineage.get("fields", {})
        if not isinstance(fields, dict):
            fields = {}

        transformations = data_lineage.get("transformations", [])
        if not isinstance(transformations, list):
            transformations = []

        processed_fields = fields.get("processed_fields", fields.get("collected_fields", []))
        if not isinstance(processed_fields, list):
            processed_fields = []

        irrelevant = [f for f in processed_fields if not any(
            isinstance(t, dict) and f in str(t) for t in transformations
        )]

        findings.append(
            DataMinFinding(
                check="data_relevance",
                passed=len(irrelevant) == 0,
                article="Art 5(1)(c)",
                detail=f"All {len(processed_fields)} fields are relevant to processing"
                if not irrelevant
                else f"Fields not referenced in transformations: {', '.join(irrelevant[:10])}",
                recommendation=f"Review relevance of unused fields: {', '.join(irrelevant[:10])}" if irrelevant else None,
                severity="WARNING" if irrelevant else "INFO",
            )
        )

        return findings

    def _check_data_necessity(
        self, data_lineage: dict[str, Any]
    ) -> list[DataMinFinding]:
        findings: list[DataMinFinding] = []
        purpose = data_lineage.get("purpose", "")
        if not isinstance(purpose, str):
            purpose = ""

        fields = data_lineage.get("fields", {})
        if not isinstance(fields, dict):
            fields = {}
        collected = fields.get("collected_fields", [])
        if not isinstance(collected, list):
            collected = []

        optional = fields.get("optional_fields", [])
        if not isinstance(optional, list):
            optional = []

        required = [f for f in collected if f not in optional]
        all_required_necessary = len(required) <= len(collected)
        findings.append(
            DataMinFinding(
                check="data_necessity",
                passed=all_required_necessary,
                article="Art 5(1)(c)",
                detail=f"Purpose: '{purpose[:100]}'. "
                f"Required fields: {len(required)}/{len(collected)}. "
                f"Optional fields identified: {len(optional)}"
                if all_required_necessary
                else "Unable to verify necessity of all required fields",
                recommendation="Document necessity justification for each required field in relation to stated purpose"
                if not all_required_necessary
                else None,
                severity="INFO",
            )
        )

        return findings

    def _check_purpose_limitation(
        self, data_lineage: dict[str, Any]
    ) -> list[DataMinFinding]:
        findings: list[DataMinFinding] = []
        purpose = data_lineage.get("purpose", "")
        if not isinstance(purpose, str):
            purpose = ""

        secondary_uses = data_lineage.get("secondary_uses", [])
        if not isinstance(secondary_uses, list):
            secondary_uses = []

        _has_compatible_secondary = True
        incompatible_secondary: list[str] = []
        for use in secondary_uses:
            if isinstance(use, dict):
                if not use.get("compatible", True):
                    incompatible_secondary.append(str(use.get("description", "unknown")))
            elif isinstance(use, str):
                pass

        findings.append(
            DataMinFinding(
                check="purpose_limitation",
                passed=len(incompatible_secondary) == 0,
                article="Art 5(1)(b)",
                detail=f"Primary purpose: '{purpose[:100]}'. "
                f"Secondary uses: {len(secondary_uses)}. "
                f"Incompatible secondary uses: {len(incompatible_secondary)}"
                if not incompatible_secondary
                else f"Incompatible secondary uses detected: {', '.join(incompatible_secondary)}",
                recommendation=f"Ensure incompatible secondary uses have separate legal basis or consent: {', '.join(incompatible_secondary)}"
                if incompatible_secondary
                else None,
                severity="WARNING" if incompatible_secondary else "INFO",
            )
        )

        return findings

    def _check_retention_periods(
        self, data_lineage: dict[str, Any]
    ) -> list[DataMinFinding]:
        findings: list[DataMinFinding] = []
        retention = data_lineage.get("retention_policies", {})
        if not isinstance(retention, dict):
            retention = {}

        fields = data_lineage.get("fields", {})
        if not isinstance(fields, dict):
            fields = {}
        collected = fields.get("collected_fields", [])
        if not isinstance(collected, list):
            collected = []

        defined_for = [f for f in collected if isinstance(retention.get(f), dict) or isinstance(retention.get(f), str)]
        undefined = [f for f in collected if f not in defined_for]

        findings.append(
            DataMinFinding(
                check="retention_periods",
                passed=len(undefined) == 0,
                article="Art 5(1)(e)",
                detail=f"Retention periods defined for {len(defined_for)}/{len(collected)} data fields. "
                f"Undefined: {', '.join(undefined[:10])}"
                if undefined
                else "Retention periods defined for all data fields",
                recommendation=f"Define retention periods for: {', '.join(undefined[:10])}"
                if undefined
                else None,
                severity="WARNING" if undefined else "INFO",
            )
        )

        for field_name, policy in retention.items():
            if isinstance(policy, dict):
                max_days = policy.get("max_days", 0)
                if max_days and isinstance(max_days, (int, float)):
                    finding = DataMinFinding(
                        check=f"retention_{field_name}",
                        passed=max_days <= 365,
                        article="Art 5(1)(e)",
                        detail=f"Retention for '{field_name}': {max_days} days"
                        if max_days <= 365
                        else f"Retention for '{field_name}': {max_days} days exceeds 1-year default recommendation",
                        recommendation=f"Reduce retention period for '{field_name}' or document legal/regulatory justification"
                        if max_days > 365
                        else None,
                        severity="WARNING" if max_days > 365 else "INFO",
                    )
                    findings.append(finding)

        return findings
