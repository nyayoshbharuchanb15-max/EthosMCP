from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI

from src.schemas.mcp_tools import load_tool_schemas
from src.services.oauth import oauth_metadata

app = FastAPI(title="EthosMCP", version="1.1.0")


@app.get("/.well-known/oauth-authorization-server")
def well_known_oauth() -> dict[str, str]:
    # Design rationale: OAuth metadata must be discoverable before any protected audit operation.
    return oauth_metadata("http://localhost:8080").__dict__


@app.get("/audit/export")
def audit_export() -> dict[str, str]:
    return {"format": "CEF", "status": "empty"}


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


def initialize_payload() -> dict[str, Any]:
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


def tools_list() -> list[dict[str, Any]]:
    return list(load_tool_schemas().values())


def run_server(*, transport: str, port: int, config_path: Path) -> None:
    _ = config_path
    if transport == "stdio":
        # Design rationale: stdio mode is for subprocess MCP clients and agent tooling.
        print(initialise_stdio_banner())
        return
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=port)


def initialise_stdio_banner() -> str:
    return "EthosMCP stdio transport ready"
