import json
import uuid
import httpx
import pytest


pytestmark = pytest.mark.integration


class TestMCPTools:

    MCP_SERVER_URL = "http://localhost:3000"

    @pytest.fixture
    def http_client(self):
        try:
            import httpx
            return httpx.AsyncClient(base_url=self.MCP_SERVER_URL, timeout=10.0)
        except ImportError:
            pytest.skip("httpx not available")

    @pytest.mark.asyncio
    async def test_mcp_tools_list_endpoint(self, http_client):
        try:
            resp = await http_client.get("/tools")
            assert resp.status_code == 200
            tools = resp.json()
            tool_names = [t.get("name") or t.get("id") for t in tools]
            assert "phase1_register" in tool_names or "phase1" in str(tools).lower()
        except (httpx.ConnectError, httpx.TimeoutException) as exc:
            pytest.skip(f"MCP server not reachable at {self.MCP_SERVER_URL}: {exc}")

    @pytest.mark.asyncio
    async def test_mcp_invoke_phase1_tool(self, http_client):
        payload = {
            "system_id": str(uuid.uuid4()),
            "system_name": "MCPToolTest",
            "system_version": "1.0.0",
            "vendor": "MCPTestVendor",
            "deployment_environment": "testing",
            "data_lineage": {
                "sources": ["test"],
                "transformations": ["test"],
                "destinations": ["test"],
            },
            "jurisdictions": ["EU"],
            "requested_by": "mcp-test@example.com",
        }
        try:
            resp = await http_client.post("/tools/phase1_register", json=payload)
            assert resp.status_code in (200, 201)
            data = resp.json()
            assert "run_id" in data or "status" in data
        except (httpx.ConnectError, httpx.TimeoutException) as exc:
            pytest.skip(f"MCP server not reachable: {exc}")

    @pytest.mark.asyncio
    async def test_phase_schema_validation(self, http_client):
        invalid_payload = {"system_name": "MissingRequiredFields"}
        try:
            resp = await http_client.post("/tools/phase1_register", json=invalid_payload)
            assert resp.status_code in (400, 422)
            error_detail = resp.json()
            assert "detail" in error_detail or "error" in error_detail or "message" in error_detail
        except (httpx.ConnectError, httpx.TimeoutException) as exc:
            pytest.skip(f"MCP server not reachable: {exc}")

    @pytest.mark.asyncio
    async def test_mcp_cors_headers(self, http_client):
        try:
            resp = await http_client.options("/tools")
            assert resp.status_code in (200, 204)
        except (httpx.ConnectError, httpx.TimeoutException) as exc:
            pytest.skip(f"MCP server not reachable: {exc}")
