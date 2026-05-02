from redis.asyncio import Redis

from .envelope import EventEnvelope


class EventPublisher:
    def __init__(self, redis: Redis) -> None:
        self._redis = redis

    async def publish(self, envelope: EventEnvelope) -> None:
        await self._redis.publish(envelope.to_topic(), envelope.model_dump_json())
