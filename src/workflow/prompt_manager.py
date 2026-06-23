from __future__ import annotations

from src.prompts import get_prompt_bundle


class PromptManager:
    def __init__(self) -> None:
        self._bundle = get_prompt_bundle()

    def resolve_tool_prompt(self, tool_name: str) -> dict[str, str]:
        return {
            "system": self._bundle["system_templates"]["default"],
            "audit_system": self._bundle["system_templates"]["audit"],
            "user": self._bundle["user_prompts"].get(tool_name, "Run metadata-only compliance audit."),
        }

    def workflow_contexts(self) -> dict[str, str]:
        return dict(self._bundle["contexts"])
