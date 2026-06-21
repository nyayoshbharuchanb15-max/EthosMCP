# src/main.py

from fastmcp import FastMCP
from src.config import settings
from src.services import governance, localization, sovereignty, security

app = FastMCP(title="EthosMCP Server", version="1.0.0")

# Register services
app.register_service(governance.router)
app.register_service(localization.router)
app.register_service(sovereignty.router)
app.register_service(security.router)

@app.on_event("startup")
async def startup_event():
    print("EthosMCP server starting up...")
    # Initialize database connections, load models, etc.

@app.on_event("shutdown")
async def shutdown_event():
    print("EthosMCP server shutting down...")
    # Close database connections, clean up resources, etc.

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT)
