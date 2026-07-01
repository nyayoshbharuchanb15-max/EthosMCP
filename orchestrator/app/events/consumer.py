import json
import asyncio
from typing import Optional
from app.config import settings
from app.logger import logger


class NATSConsumer:
    _client: Optional[asyncio.Event] = None

    def __init__(self):
        self.server = settings.nats_url
        self.nc = None
        self.js = None

    async def connect(self):
        try:
            import nats
            self.nc = await nats.connect(self.server)
            self.js = self.nc.jetstream()
            logger.info("NATS Consumer connected")
        except Exception as e:
            logger.warning("NATS Consumer unavailable", error=str(e))

    async def listen_phase_completions(self):
        """Listen for async phase completion events."""
        if not self.js:
            logger.warning("JetStream unavailable, skipping consumer")
            return

        try:
            _ = await self.js.stream_info("audit_events")
        except Exception:
            await self.js.add_stream(name="audit_events", subjects=["audit.*"])

        async def callback(msg):
            data = json.loads(msg.data.decode())
            logger.info("Consumer received event", subject=msg.subject, data=data)

            if msg.subject == "audit.phase.completed":
                run_id = data.get("run_id")
                phase = data.get("phase")
                status = data.get("status")
                if status == "BLOCKER":
                    logger.warning("Blocker detected in async phase", run_id=run_id, phase=phase)

            elif msg.subject == "audit.drift.detected":
                run_id = data.get("run_id")
                logger.info("Drift alert received, triggering reaudit", run_id=run_id)

            await msg.ack()

        await self.js.subscribe("audit.*", cb=callback)
        logger.info("Listening for audit events")

    async def close(self):
        if self.nc:
            await self.nc.close()
