from fastapi import FastAPI
from routers import audit, certificates, health
import uvicorn

app = FastAPI(
    title="AI Governance Audit API",
    description="Python FastAPI backend for 9-phase AI regulatory auditing",
    version="1.0.0"
)

# Include Routers
app.include_router(audit.router)
app.include_router(certificates.router)
app.include_router(health.router)

@app.get("/")
async def root():
    return {"message": "AI Governance Audit API is running"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
