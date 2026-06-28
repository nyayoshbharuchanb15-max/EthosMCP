class ReauditTrigger:
    def should_trigger(self, drift_report: dict) -> bool:
        return drift_report.get("drift_detected", False)
