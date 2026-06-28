class WebhookSubscriber:
    """
    Subscribes to events from NATS or Redis Streams.
    """
    def __init__(self, nats_url: str):
        self.nats_url = nats_url

    def listen(self, topic: str):
        print(f"Listening on {topic}...")
        # NATS subscribe logic would go here

if __name__ == "__main__":
    sub = WebhookSubscriber("nats://localhost:4222")
    sub.listen("audit.drift_detected")
