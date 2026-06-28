import json

class WebhookPublisher:
    """
    Publishes events to NATS or Redis Streams.
    """
    def __init__(self, nats_url: str):
        self.nats_url = nats_url

    def publish(self, topic: str, data: dict):
        print(f"Publishing to {topic}: {json.dumps(data)}")
        # NATS publish logic would go here

if __name__ == "__main__":
    pub = WebhookPublisher("nats://localhost:4222")
    pub.publish("audit.drift_detected", {"model_id": "model_123"})
