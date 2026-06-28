from models.audit_models import DPIAInput, DPIAReport

class DPIAGeneratorService:
    def generate(self, input_data: DPIAInput) -> DPIAReport:
        conflicts = []
        if input_data.storage_location == "outside_eu" and "Standard Contractual Clauses" not in input_data.transfer_mechanisms:
            conflicts.append("Data stored outside EU without SCCs")
            
        return DPIAReport(
            risk_level="Medium" if conflicts else "Low",
            jurisdictional_conflicts=conflicts,
            mitigation_measures=["Implement TLS 1.3", "Data minimization", "Pseudonymization"],
            explanation="DPIA generated per GDPR Art. 35. Assessment of measures envisaged to address risks to data subjects.",
            regulatory_basis=["GDPR Art. 35", "GDPR Art. 35(7)(d)", "GDPR Art. 44-49"]
        )
