from models.audit_models import SupplyChainInput, ProvenanceReport

class SupplyChainService:
    def audit(self, input_data: SupplyChainInput) -> ProvenanceReport:
        # Mock logic for provenance tracing
        risk_score = 15.0 # Low risk
        if any("unverified" in ds.lower() for ds in input_data.data_sources):
            risk_score += 40.0
            
        return ProvenanceReport(
            ip_risk_score=risk_score,
            lineage_complete=risk_score < 50,
            findings=[f"Audited {len(input_data.data_sources)} data sources", "IP clearance verified for base model"],
            explanation="Supply chain audit completed. Data lineage traced and IP risks assessed per GDPR Art. 5 and ISO 42001.",
            regulatory_basis=["GDPR Art. 5", "ISO 42001 Clause 6"]
        )
