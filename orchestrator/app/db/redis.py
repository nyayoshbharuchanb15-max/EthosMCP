import json
from typing import Optional
from redis.asyncio import Redis as AsyncRedis
from app.config import settings


class RedisClient:
    _client: Optional[AsyncRedis] = None

    @classmethod
    async def connect(cls) -> AsyncRedis:
        if cls._client is None:
            cls._client = AsyncRedis.from_url(
                settings.redis_url,
                decode_responses=True,
            )
            await cls._client.ping()
        return cls._client

    @classmethod
    async def close(cls):
        if cls._client:
            await cls._client.close()
            cls._client = None

    @classmethod
    async def cache_run_state(cls, run_id: str, state: dict, ttl: int = 3600):
        client = await cls.connect()
        await client.setex(f"run_state:{run_id}", ttl, json.dumps(state))

    @classmethod
    async def get_run_state(cls, run_id: str) -> Optional[dict]:
        client = await cls.connect()
        data = await client.get(f"run_state:{run_id}")
        if data:
            return json.loads(data)
        return None

    @classmethod
    async def flush_subject_cache(cls, email_hash: str):
        client = await cls.connect()
        cursor = 0
        while True:
            cursor, keys = await client.scan(cursor, match=f"*{email_hash}*", count=100)
            if keys:
                await client.delete(*keys)
            if cursor == 0:
                break
