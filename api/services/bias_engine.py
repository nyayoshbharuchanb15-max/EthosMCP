from models.audit_models import BiasAssessmentInput, BiasReport

class BiasEngineService:
    def assess(self, input_data: BiasAssessmentInput) -> BiasReport:
        # Mock results from Fairlearn/AIF360
        disparity = {cls: 0.05 for cls in input_data.protected_classes}
        if "race" in input_data.protected_classes:
            disparity["race"] = 0.12 # Example higher disparity
            
        return BiasReport(
            disparity_scores=disparity,
            findings=["Demographic parity difference within acceptable bounds for most classes", "Minor disparity detected in 'race' class"],
            worst_performing_group="race",
            explanation="Multidimensional bias scan performed. Metrics within tolerance for 4/5 protected classes per EU AI Act Art. 10(2)(f).",
            regulatory_basis=["EU AI Act Art. 10(2)(f)", "NIST AI RMF Map Function"]
        )
