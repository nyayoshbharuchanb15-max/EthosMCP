from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import Body, FastAPI, HTTPException

from src.config import settings
from src.models.workflow import AuditWorkflowRequest
from src.services.oauth import oauth_metadata
from src.workflow import ResourceOrchestrator

app = FastAPI(title="EthosMCP", version=settings.version)
orchestrator = ResourceOrchestrator()


@app.get("/.well-known/oauth-authorization-server")
def well_known_oauth() -> dict[str, str]:
    return oauth_metadata(settings.base_url).__dict__


@app.get("/audit/export")
def audit_export() -> dict[str, str]:
    return {"format": "CEF", "status": "metadata-only"}


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/tools/list")
def tools_list_endpoint() -> list[dict[str, Any]]:
    return orchestrator.list_registered_tools()


@app.post("/tools/invoke/{tool_name}")
async def tools_invoke_endpoint(tool_name: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    try:
        return await orchestrator.run_tool(tool_name, payload)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/workflow/snapshot")
def workflow_snapshot_endpoint() -> dict[str, Any]:
    return orchestrator.workflow_snapshot()


@app.post("/audit/workflow")
async def audit_workflow_endpoint(
    payload: AuditWorkflowRequest = Body(default_factory=AuditWorkflowRequest),
) -> dict[str, Any]:
    return await orchestrator.run_audit_workflow(payload.model_dump())


@app.post("/mcp/initialize")
def initialize_endpoint() -> dict[str, Any]:
    return {
        "protocolVersion": "2025-06-18",
        "capabilities": {
            "tools": {"listChanged": True},
            "resources": {"subscribe": False, "listChanged": False},
            "prompts": {"listChanged": False},
            "logging": {},
        },
        "serverInfo": {"name": settings.app_name, "version": settings.version},
    }


def initialize_payload() -> dict[str, Any]:
    return initialize_endpoint()


def tools_list() -> list[dict[str, Any]]:
    return orchestrator.list_registered_tools()


def run_server(*, transport: str, port: int, config_path: Path) -> None:
    _ = config_path
    if transport == "stdio":
        from src.mcp_app import mcp

        mcp.run(transport="stdio")
        return

    # HTTP mode: mount the MCP streamable-HTTP transport alongside the REST API so
    # that both curl/browser clients (via /tools/invoke/*) and MCP-aware AI clients
    # (Claude Desktop, Cursor — via /mcp) can reach the server on the same port.
    from src.mcp_app import mcp

    app.mount("/mcp", mcp.streamable_http_app())

    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=port)
