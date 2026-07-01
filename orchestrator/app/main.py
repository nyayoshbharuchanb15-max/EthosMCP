from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.config import settings
from app.logger import logger
from app.db.postgres import init_db
from app.db.neo4j import Neo4jClient
from app.db.redis import RedisClient
from app.routers import audit, certificate, dsar, ropa


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting orchestrator", version=settings.app_version)

    # Initialize database
    try:
        await init_db()
        logger.info("PostgreSQL initialized")
    except Exception as e:
        logger.warning("PostgreSQL init failed (may not be available)", error=str(e))

    # Connect Neo4j
    try:
        await Neo4jClient.connect()
        logger.info("Neo4j connected")
    except Exception as e:
        logger.warning("Neo4j connection failed", error=str(e))

    # Connect Redis
    try:
        await RedisClient.connect()
        logger.info("Redis connected")
    except Exception as e:
        logger.warning("Redis connection failed", error=str(e))

    yield

    # Cleanup
    await Neo4jClient.close()
    await RedisClient.close()
    logger.info("Orchestrator shutdown")


app = FastAPI(
    title=settings.app_name,
    description="9-phase AI compliance audit pipeline orchestrator",
    version=settings.app_version,
    lifespan=lifespan,
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info("request", method=request.method, path=request.url.path)
    try:
        response = await call_next(request)
        logger.info("response", status=response.status_code, path=request.url.path)
        return response
    except Exception as exc:
        logger.exception("unhandled error", path=request.url.path)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error", "error": str(exc)},
        )


# Include routers
app.include_router(audit.router)
app.include_router(certificate.router)
app.include_router(dsar.router)
app.include_router(ropa.router)


@app.get("/")
async def root():
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "version": settings.app_version,
        "timestamp": __import__("datetime").datetime.utcnow().isoformat() + "Z",
    }
