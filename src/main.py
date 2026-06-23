# src/main.py

from fastmcp import FastMCP
from src.config import settings
from src.services import governance, localization, sovereignty, security

# Initialize FastMCP application
mcp = FastMCP(title="EthosMCP Server", version="1.0.0")

# Register tools directly on the mcp instance using the logic from service modules
# Governance Tools
@mcp.tool()
async def get_ropa_records():
    """Accesses foundational data classification mapping tables."""
    return await governance.get_ropa_records()

@mcp.tool()
async def audit_ropa_alignment():
    """Verifies ROPA alignment and purpose limitation."""
    return await governance.audit_ropa_alignment()

# Localization Tools
@mcp.tool()
async def analyze_data_flow():
    """Examines infrastructural network boundaries and regional compliance."""
    return await localization.analyze_data_flow()

# Sovereignty Tools
@mcp.tool()
async def query_consent_registry():
    """Audits the structural integrity of the front-end consent lifecycle."""
    return await sovereignty.query_consent_registry()

@mcp.tool()
async def simulate_dsar_workflow(user_id: str, request_type: str, erasure_latency_days: int = 0):
    """Evaluates system capacity to fulfill individual access and erasure requests."""
    dsar_request = {
        "user_id": user_id,
        "request_type": request_type,
        "erasure_latency_days": erasure_latency_days
    }
    return await sovereignty.simulate_dsar_workflow(dsar_request)

# Security Tools
@mcp.tool()
async def audit_encryption_coverage():
    """Verifies encryption coverage for data at rest and in transit."""
    return await security.audit_encryption_coverage()

if __name__ == "__main__":
    mcp.run()
