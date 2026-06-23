from __future__ import annotations

from dataclasses import asdict, is_dataclass
from inspect import signature
from typing import Any, Awaitable, Callable, cast

from src.schemas.mcp_tools import load_tool_schemas
from src.services import governance, localization, security, sovereignty
from src.services import data_purpose
from src.workflow.audit_protocol import run_audit_workflow

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
            "verify_data_purpose": data_purpose.verify_data_purpose,
            "run_audit_workflow": run_audit_workflow,
        }
        missing_schemas = [tool_name for tool_name in self._tools if tool_name not in self._schemas]
        if missing_schemas:
            raise ValueError(f"Missing schemas for registered tools: {', '.join(sorted(missing_schemas))}")

    def list_tools(self) -> list[dict[str, Any]]:
        return [self._schemas[tool_name] for tool_name in self._tools if tool_name in self._schemas]

    async def invoke(self, name: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        if name not in self._tools:
            raise KeyError(f"Unknown tool: {name}")
        payload = payload or {}
        tool_callable = self._tools[name]
        parameters = signature(tool_callable).parameters.values()
        requires_payload = any(
            parameter.default is parameter.empty
            for parameter in parameters
            if parameter.kind in {parameter.POSITIONAL_ONLY, parameter.POSITIONAL_OR_KEYWORD, parameter.KEYWORD_ONLY}
        )
        if requires_payload:
            result = await tool_callable(payload)
        else:
            result = await tool_callable()

        if is_dataclass(result) and not isinstance(result, type):
            return asdict(result)
        if isinstance(result, dict):
            return cast(dict[str, Any], result)
        raise TypeError(f"Tool {name} returned unsupported result type: {type(result).__name__}")
