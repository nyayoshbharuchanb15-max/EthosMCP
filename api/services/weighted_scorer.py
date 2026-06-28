from models.audit_models import WeightedScoreInput, WeightedAuditScore
from typing import Dict

class WeightedScorerService:
    def calculate(self, input_data: WeightedScoreInput) -> WeightedAuditScore:
        """
        Aggregates phase results into a weighted score per NIST AI RMF.
        """
        # Weight configuration
        weights = {
            "risk_classification": 0.20,
            "supply_chain": 0.15,
            "human_oversight": 0.25,
            "bias_assessment": 0.15,
            "dpia_generation": 0.10,
            "adversarial_testing": 0.15
        }
        
        scores: Dict[str, float] = {}
        # Mock scoring logic based on presence and content of results
        for phase_result in input_data.phase_results:
            tool = phase_result.get("tool_name")
            if tool == "classify_ai_risk":
                scores["risk_classification"] = 100.0 if phase_result.get("result", {}).get("tier") != "PROHIBITED" else 0.0
            elif tool == "verify_human_oversight":
                scores["human_oversight"] = 100.0 if phase_result.get("result", {}).get("result") == "PASS" else 0.0
            # ... other phases ...
            
        # Default scores for missing phases for mock purposes
        for key in weights:
            if key not in scores:
                scores[key] = 90.0 # Default "good" score for mock
        
        overall_score = sum(scores[k] * weights[k] for k in weights)
        blocking = overall_score < 60.0 or scores.get("human_oversight") == 0.0
        
        return WeightedAuditScore(
            overall_score=overall_score,
            score_breakdown=scores,
            compliance_status="Compliant" if not blocking else "Non-Compliant",
            blocking=blocking,
            explanation=f"Overall risk-weighted score of {overall_score:.2f}%. " + 
                        ("Audit passed minimum threshold." if not blocking else "BLOCKER_FAIL: Score below threshold or critical failure detected."),
            regulatory_basis=["NIST AI RMF Measure Function"]
        )
