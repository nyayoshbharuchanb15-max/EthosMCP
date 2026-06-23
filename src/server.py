from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI

from src.schemas.mcp_tools import load_tool_schemas
from src.services.oauth import oauth_metadata

app = FastAPI(title="EthosMCP", version="1.1.0")
SCHEMA_CACHE = load_tool_schemas()


@app.get("/.well-known/oauth-authorization-server")
def well_known_oauth() -> dict[str, str]:
    # Design rationale: OAuth discovery must be publicly visible before protected tool access.
    return oauth_metadata("http://localhost:8080").__dict__


@app.get("/audit/export")
def audit_export() -> dict[str, str]:
    return {"format": "CEF", "status": "empty"}


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/tools/list")
def tools_list_endpoint() -> list[dict[str, Any]]:
    return list(SCHEMA_CACHE.values())


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
        "serverInfo": {"name": "EthosMCP", "version": "1.0.0"},
    }


def initialize_payload() -> dict[str, Any]:
    return initialize_endpoint()


def tools_list() -> list[dict[str, Any]]:
    return list(SCHEMA_CACHE.values())


def run_server(*, transport: str, port: int, config_path: Path) -> None:
    _ = config_path
    if transport == "stdio":
        # Design rationale: stdio transport is for subprocess-based MCP clients and local agents.
        print("EthosMCP stdio transport ready")
        return
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=port)
