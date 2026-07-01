import json
import asyncio
from typing import Optional
from app.config import settings
from app.logger import logger


class NATSProducer:
    _client: Optional[asyncio.Event] = None  # Placeholder for actual NATS client

    def __init__(self):
        self.server = settings.nats_url
        self.nc = None
        self.js = None

    async def connect(self):
        try:
            import nats
            self.nc = await nats.connect(self.server)
            self.js = self.nc.jetstream()
            logger.info("Connected to NATS JetStream", server=self.server)
        except ImportError:
            logger.warning("nats-py not installed, using fallback")
        except Exception as e:
            logger.error("NATS connection failed", error=str(e))

    async def publish(self, subject: str, data: dict):
        if self.js:
            await self.js.publish(subject, json.dumps(data).encode())
            logger.info("Published event", subject=subject)
        else:
            logger.info("NATS unavailable — event logged", subject=subject, data=data)

    async def close(self):
        if self.nc:
            await self.nc.close()

    async def publish_phase_complete(self, run_id: str, phase: int, status: str):
        await self.publish(
            "audit.phase.completed",
            {"run_id": run_id, "phase": phase, "status": status},
        )

    async def publish_drift_alert(self, run_id: str, model_id: str, metrics: dict):
        await self.publish(
            "audit.drift.detected",
            {"run_id": run_id, "model_id": model_id, "metrics": metrics},
        )

    async def publish_certificate_issued(self, run_id: str, cert_id: str):
        await self.publish(
            "audit.certificate.issued",
            {"run_id": run_id, "cert_id": cert_id},
        )

    async def publish_reaudit_triggered(self, original_run_id: str, new_run_id: str):
        await self.publish(
            "audit.reaudit.triggered",
            {"original_run_id": original_run_id, "new_run_id": new_run_id},
        )
