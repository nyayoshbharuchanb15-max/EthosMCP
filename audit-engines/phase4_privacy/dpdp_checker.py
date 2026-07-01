from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class DPDPFinding(BaseModel):
    section: str
    passed: bool
    detail: str
    remediation: str | None = None
    severity: str = "INFO"


class DPDPCheckResult(BaseModel):
    findings: list[DPDPFinding] = Field(default_factory=list)
    compliant: bool = False
    overall_score: float = 0.0


LEGITIMATE_GROUNDS_SECTION_4: list[str] = [
    "consent",
    "performance_of_contract",
    "legal_obligation",
    "vital_interests",
    "public_task",
    "legitimate_interests",
]

SIGNIFICANT_DATA_FIDUCIARY_CRITERIA: list[str] = [
    "volume_of_data_processed_exceeds_threshold",
    "sensitivity_of_data_processed",
    "impact_on_data_subject_rights",
    "turnover_or_revenue_threshold",
    "use_of_new_or_emerging_technologies",
    "cross_border_data_transfer_volume",
    "processing_of_children_data",
]


class DPDPActChecker:
    def check(self, processing_profile: dict[str, Any]) -> DPDPCheckResult:
        findings: list[DPDPFinding] = []

        finding_grounds = self._check_grounds_for_processing(processing_profile)
        findings.extend(finding_grounds)

        finding_notice = self._check_notice_obligations(processing_profile)
        findings.extend(finding_notice)

        finding_fiduciary = self._check_fiduciary_obligations(processing_profile)
        findings.extend(finding_fiduciary)

        finding_sdf = self._check_significant_data_fiduciary(processing_profile)
        findings.extend(finding_sdf)

        finding_children = self._check_childrens_data(processing_profile)
        findings.extend(finding_children)

        finding_rights = self._check_data_subject_rights(processing_profile)
        findings.extend(finding_rights)

        passed_count = sum(1 for f in findings if f.passed)
        overall_score = passed_count / len(findings) if findings else 0.0
        compliant = overall_score >= 0.8

        return DPDPCheckResult(
            findings=findings,
            compliant=compliant,
            overall_score=round(overall_score, 2),
        )

    def _check_grounds_for_processing(
        self, profile: dict[str, Any]
    ) -> list[DPDPFinding]:
        findings: list[DPDPFinding] = []
        grounds = profile.get("grounds_for_processing", [])
        if not isinstance(grounds, list):
            grounds = [str(grounds)] if grounds else []

        has_valid_ground = any(g in LEGITIMATE_GROUNDS_SECTION_4 for g in grounds)
        findings.append(
            DPDPFinding(
                section="Sec 4-6",
                passed=has_valid_ground,
                detail="Processing must be based on one or more legitimate grounds under DPDP Act Sec 4-6",
                remediation="Ensure processing has a valid lawful basis: consent, contract, legal obligation, "
                "vital interests, public task, or legitimate interests."
                if not has_valid_ground
                else None,
                severity="BLOCKER" if not has_valid_ground else "INFO",
            )
        )

        if "consent" in grounds:
            consent_type = profile.get("consent_type", "")
            findings.append(
                DPDPFinding(
                    section="Sec 4-6",
                    passed=consent_type in ("explicit", "unambiguous", "affirmative"),
                    detail="Consent must be free, specific, informed, and unambiguous with clear affirmative action",
                    remediation="Implement granular consent mechanisms with clear opt-in and withdrawal capabilities."
                    if consent_type not in ("explicit", "unambiguous", "affirmative")
                    else None,
                    severity="WARNING",
                )
            )

        return findings

    def _check_notice_obligations(
        self, profile: dict[str, Any]
    ) -> list[DPDPFinding]:
        findings: list[DPDPFinding] = []
        notice = profile.get("privacy_notice", {})
        if not isinstance(notice, dict):
            notice = {}

        has_notice = bool(notice.get("provided", False))
        findings.append(
            DPDPFinding(
                section="Sec 7",
                passed=has_notice,
                detail="Data Fiduciary must provide a privacy notice at the time of collection or before processing",
                remediation="Draft and provide a comprehensive privacy notice covering all Sec 7 requirements."
                if not has_notice
                else None,
                severity="BLOCKER" if not has_notice else "INFO",
            )
        )

        if has_notice:
            required_fields = [
                "purpose_of_processing",
                "categories_of_data",
                "rights_of_data_subject",
                "retention_period",
                "grievance_officer_contact",
            ]
            missing = [f for f in required_fields if not notice.get(f)]
            findings.append(
                DPDPFinding(
                    section="Sec 7(a)-(e)",
                    passed=len(missing) == 0,
                    detail=f"Notice must include: purpose, data categories, rights, retention, grievance contact. "
                    f"Missing: {', '.join(missing)}" if missing else "All required notice elements present",
                    remediation=f"Add missing fields to privacy notice: {', '.join(missing)}"
                    if missing
                    else None,
                    severity="WARNING" if missing else "INFO",
                )
            )

        language = notice.get("language", "")
        findings.append(
            DPDPFinding(
                section="Sec 7",
                passed=bool(language) and language in ("english", "hindi", "regional"),
                detail="Notice must be in English and/or languages understood by the data subject",
                remediation="Provide notice in English and regional languages as applicable."
                if not language
                else None,
                severity="WARNING",
            )
        )

        return findings

    def _check_fiduciary_obligations(
        self, profile: dict[str, Any]
    ) -> list[DPDPFinding]:
        findings: list[DPDPFinding] = []
        obligations = profile.get("data_fiduciary_obligations", {})
        if not isinstance(obligations, dict):
            obligations = {}

        has_dpo = bool(obligations.get("dpo_appointed", False))
        findings.append(
            DPDPFinding(
                section="Sec 8",
                passed=has_dpo,
                detail="Data Fiduciary must appoint a Data Protection Officer (DPO) per Sec 8",
                remediation="Designate a DPO and publish contact details in the privacy notice."
                if not has_dpo
                else None,
                severity="WARNING" if not has_dpo else "INFO",
            )
        )

        has_grievance = bool(obligations.get("grievance_redressal_mechanism", False))
        findings.append(
            DPDPFinding(
                section="Sec 8",
                passed=has_grievance,
                detail="Data Fiduciary must establish an effective grievance redressal mechanism per Sec 8",
                remediation="Establish a grievance redressal mechanism with a designated officer responding within 7 days."
                if not has_grievance
                else None,
                severity="WARNING" if not has_grievance else "INFO",
            )
        )

        data_audit = bool(obligations.get("data_audit_conducted", False))
        findings.append(
            DPDPFinding(
                section="Sec 8",
                passed=data_audit,
                detail="Data Fiduciary must conduct periodic data audits per Sec 8",
                remediation="Implement periodic data audit processes to verify compliance with DPDP Act."
                if not data_audit
                else None,
                severity="WARNING" if not data_audit else "INFO",
            )
        )

        return findings

    def _check_significant_data_fiduciary(
        self, profile: dict[str, Any]
    ) -> list[DPDPFinding]:
        findings: list[DPDPFinding] = []
        sdf_info = profile.get("significant_data_fiduciary", {})
        if not isinstance(sdf_info, dict):
            sdf_info = {}

        is_sdf_candidate = False
        for criterion in SIGNIFICANT_DATA_FIDUCIARY_CRITERIA:
            if sdf_info.get(criterion, False):
                is_sdf_candidate = True
                break

        if is_sdf_candidate:
            registered = bool(sdf_info.get("registered_as_sdf", False))
            findings.append(
                DPDPFinding(
                    section="Sec 9",
                    passed=registered,
                    detail="Entity meets Significant Data Fiduciary criteria and must register with DPA per Sec 9",
                    remediation="Apply for registration as Significant Data Fiduciary with the Data Protection Authority."
                    if not registered
                    else None,
                    severity="BLOCKER" if not registered else "INFO",
                )
            )

            has_dpia = bool(sdf_info.get("dpia_conducted", False))
            findings.append(
                DPDPFinding(
                    section="Sec 9",
                    passed=has_dpia,
                    detail="Significant Data Fiduciary must conduct Data Protection Impact Assessments per Sec 9",
                    remediation="Conduct DPIA for all high-risk processing activities."
                    if not has_dpia
                    else None,
                    severity="WARNING" if not has_dpia else "INFO",
                )
            )

            independent_auditor = bool(sdf_info.get("independent_auditor_appointed", False))
            findings.append(
                DPDPFinding(
                    section="Sec 9",
                    passed=independent_auditor,
                    detail="Significant Data Fiduciary must appoint an independent data auditor per Sec 9",
                    remediation="Appoint an independent data auditor to assess compliance annually."
                    if not independent_auditor
                    else None,
                    severity="WARNING" if not independent_auditor else "INFO",
                )
            )
        else:
            findings.append(
                DPDPFinding(
                    section="Sec 9",
                    passed=True,
                    detail="Entity does not meet Significant Data Fiduciary criteria based on current profile",
                    severity="INFO",
                )
            )

        return findings

    def _check_childrens_data(self, profile: dict[str, Any]) -> list[DPDPFinding]:
        findings: list[DPDPFinding] = []
        children = profile.get("children_data_processing", {})
        if not isinstance(children, dict):
            children = {}

        processes_children = bool(children.get("processes_children_data", False))
        if not processes_children:
            findings.append(
                DPDPFinding(
                    section="Sec 16",
                    passed=True,
                    detail="No processing of children's data detected",
                    severity="INFO",
                )
            )
            return findings

        parental_consent = bool(children.get("parental_consent_obtained", False))
        findings.append(
            DPDPFinding(
                section="Sec 16",
                passed=parental_consent,
                detail="Processing of children's data requires verifiable parental consent per Sec 16",
                remediation="Implement verifiable parental consent mechanisms for all data subjects under 18."
                if not parental_consent
                else None,
                severity="BLOCKER" if not parental_consent else "INFO",
            )
        )

        age_verification = bool(children.get("age_verification_implemented", False))
        findings.append(
            DPDPFinding(
                section="Sec 16",
                passed=age_verification,
                detail="Data Fiduciary must implement age verification mechanisms per Sec 16",
                remediation="Deploy age-gating and age verification solutions to identify minor data subjects."
                if not age_verification
                else None,
                severity="BLOCKER" if not age_verification else "INFO",
            )
        )

        prohibition = bool(children.get("prohibited_processing", False))
        findings.append(
            DPDPFinding(
                section="Sec 16",
                passed=not prohibition,
                detail="Certain types of processing of children's data are prohibited under Sec 16",
                remediation="Review processing activities and cease any tracking or behavioural monitoring of children."
                if prohibition
                else None,
                severity="BLOCKER" if prohibition else "INFO",
            )
        )

        return findings

    def _check_data_subject_rights(
        self, profile: dict[str, Any]
    ) -> list[DPDPFinding]:
        findings: list[DPDPFinding] = []
        rights = profile.get("data_subject_rights", {})
        if not isinstance(rights, dict):
            rights = {}

        right_to_access = bool(rights.get("right_to_access_implemented", False))
        findings.append(
            DPDPFinding(
                section="Sec 11",
                passed=right_to_access,
                detail="Data subjects have the right to access their personal data per Sec 11",
                remediation="Implement self-service data access portal or automated response to access requests."
                if not right_to_access
                else None,
                severity="WARNING" if not right_to_access else "INFO",
            )
        )

        right_to_correction = bool(rights.get("right_to_correction_implemented", False))
        findings.append(
            DPDPFinding(
                section="Sec 12",
                passed=right_to_correction,
                detail="Data subjects have the right to correction and erasure per Sec 12",
                remediation="Implement mechanisms for data subjects to request correction or erasure of their data."
                if not right_to_correction
                else None,
                severity="WARNING" if not right_to_correction else "INFO",
            )
        )

        right_to_grievance = bool(rights.get("grievance_redressal_implemented", False))
        findings.append(
            DPDPFinding(
                section="Sec 13",
                passed=right_to_grievance,
                detail="Data subjects have the right to grievance redressal per Sec 13",
                remediation="Establish a grievance redressal mechanism that responds within 7 days of receipt."
                if not right_to_grievance
                else None,
                severity="WARNING" if not right_to_grievance else "INFO",
            )
        )

        right_to_nomination = bool(rights.get("right_to_nomination_implemented", False))
        findings.append(
            DPDPFinding(
                section="Sec 14",
                passed=right_to_nomination,
                detail="Data subjects have the right to nominate a representative per Sec 14",
                remediation="Provide functionality for data subjects to register a nominee who can exercise rights posthumously."
                if not right_to_nomination
                else None,
                severity="WARNING" if not right_to_nomination else "INFO",
            )
        )

        return findings
