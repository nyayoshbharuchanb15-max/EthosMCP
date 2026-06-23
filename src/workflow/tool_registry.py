from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any, Awaitable, Callable

from src.schemas.mcp_tools import load_tool_schemas
from src.services import governance, localization, security, sovereignty

ToolCallable = Callable[..., Awaitable[Any]]


class ToolRegistry:
    def __init__(self) -> None:
        self._schemas = load_tool_schemas()
        self._tools: dict[str, ToolCallable] = {
            "get_ropa_records": governance.get_ropa_records,
            "audit_ropa_alignment": governance.audit_ropa_alignment,
            "analyze_data_flow": localization.analyze_data_flow,
            "query_consent_registry": sovereignty.query_consent_registry,
            "simulate_dsar_workflow": sovereignty.simulate_dsar_workflow,
            "audit_encryption_coverage": security.audit_encryption_coverage,
        }

    def list_tools(self) -> list[dict[str, Any]]:
        listed = list(self._schemas.values())
        for tool_name in self._tools:
            if tool_name not in self._schemas:
                listed.append({"name": tool_name, "description": "Registered compliance tool"})
        return listed

    async def invoke(self, name: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        if name not in self._tools:
            raise KeyError(f"Unknown tool: {name}")
        payload = payload or {}
        if name == "simulate_dsar_workflow":
            result = await self._tools[name](payload)
        else:
            result = await self._tools[name]()

        if is_dataclass(result):
            return asdict(result)
        return result
