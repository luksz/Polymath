from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from .envelope import EventEnvelope


class OutboxWriter:
    """Writes events to the service outbox table within the current transaction."""

    def __init__(self, schema: str) -> None:
        self._schema = schema

    async def write(self, session: AsyncSession, envelope: EventEnvelope) -> None:
        await session.execute(
            text(
                f"INSERT INTO {self._schema}.outbox (topic, payload) "
                "VALUES (:topic, :payload::jsonb)"
            ),
            {"topic": envelope.to_topic(), "payload": envelope.model_dump_json()},
        )
