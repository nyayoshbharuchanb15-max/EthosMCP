from app.state_machine.pipeline import PipelineStateMachine
from app.logger import logger


class ReauditManager:
    """
    Manages selective reaudit patterns — only re-runs phases whose
    inputs are affected by changed components.
    """

    @staticmethod
    async def should_reaudit(drift_metrics: dict, thresholds: dict) -> bool:
        """Determine if any drift metric exceeds its threshold."""
        for metric, value in drift_metrics.items():
            threshold = thresholds.get(metric, 0.1)
            if value > threshold:
                return True
        return False

    @staticmethod
    async def execute_reaudit(
        original_run_id: str,
        changed_components: list[str],
    ) -> str:
        """
        Execute selective reaudit.
        1. Query Neo4j for phases that reference changed_components
        2. Create new audit run with only those phases
        3. Retain PASS status for unaffected phases from original run
        """
        logger.info("Initiating selective reaudit",
                     original_run_id=original_run_id,
                     changed_components=changed_components)

        new_run_id = await PipelineStateMachine.trigger_reaudit(
            original_run_id, changed_components,
        )

        logger.info("Reaudit created",
                     original_run_id=original_run_id,
                     new_run_id=new_run_id,
                     changed_components=changed_components)

        return new_run_id
