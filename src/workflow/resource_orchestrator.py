from __future__ import annotations

from typing import Any

from .context_engine import ContextEngine
from .prompt_manager import PromptManager
from .tool_registry import ToolRegistry


class ResourceOrchestrator:
    def __init__(self) -> None:
        self.context_engine = ContextEngine()
        self.prompt_manager = PromptManager()
        self.tool_registry = ToolRegistry()

    def list_registered_tools(self) -> list[dict[str, Any]]:
        return self.tool_registry.list_tools()

    def workflow_snapshot(self) -> dict[str, Any]:
        return {
            "contexts": self.prompt_manager.workflow_contexts(),
            "tools": [tool.get("name") for tool in self.list_registered_tools()],
            "mode": "read-only-metadata",
        }

    async def run_tool(self, name: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        return {
            "context": self.context_engine.build_context(name),
            "prompts": self.prompt_manager.resolve_tool_prompt(name),
            "result": await self.tool_registry.invoke(name, payload),
        }
