import asyncio
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio

# Initialize Server
server = Server("ethosmcp-server")

# 1. MCP RESOURCES (Static context for the LLM)
@server.list_resources()
async def handle_list_resources() -> list[types.Resource]:
    return [
        types.Resource(
            uri=types.AnyUrl("policy://eu-ai-act-summary"),
            name="EU AI Act Summary",
            description="Core compliance rules for EthosMCP",
            mimeType="text/plain",
        )
    ]

@server.read_resource()
async def handle_read_resource(uri: types.AnyUrl) -> str:
    if uri.scheme == "policy":
        return "POLICY DOCUMENT: All AI requests must verify data lineage and purpose limitation before execution. Zero-trust architecture enforced."
    raise ValueError(f"Unsupported URI: {uri}")

# 2. MCP TOOLS (Executable functions for the LLM)
@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="verify_data_purpose",
            description="Check if an AI request aligns with the allowed data usage purpose.",
            inputSchema={
                "type": "object",
                "properties": {
                    "dataset_id": {"type": "string"},
                    "requested_purpose": {"type": "string"}
                },
                "required": ["dataset_id", "requested_purpose"],
            },
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> list[types.TextContent]:
    if name == "verify_data_purpose":
        if arguments is None:
            raise ValueError("arguments must not be null for verify_data_purpose")
        dataset = arguments.get('dataset_id')
        purpose = arguments.get('requested_purpose')
        # TODO: integrate with src/services/data_purpose.py for real compliance
        # verification against the dataset-purpose registry.
        return [types.TextContent(
            type="text",
            text=(
                f"[STUB] Purpose check for dataset '{dataset}' with purpose '{purpose}' "
                "is not yet implemented in the standalone server. "
                "Integrate with src/services/data_purpose.py for real compliance verification."
            ),
        )]
    raise ValueError(f"Unknown tool: {name}")

# 3. INITIALIZATION & TRANSPORT (stdio)
async def main():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="ethosmcp-server",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
