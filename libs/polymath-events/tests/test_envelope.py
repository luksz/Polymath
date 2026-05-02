import uuid
from datetime import timezone

from polymath_events.envelope import Actor, EventEnvelope


def test_event_id_is_auto_generated_uuid():
    env = EventEnvelope(
        event_type="notes.note.created",
        actor=Actor(type="user", id="user-123"),
        data={"note_id": "abc"},
    )
    # Should parse without error
    assert uuid.UUID(env.event_id)


def test_to_topic_returns_event_type():
    env = EventEnvelope(
        event_type="habits.checkin.created",
        actor=Actor(type="user", id="u1"),
        data={},
    )
    assert env.to_topic() == "habits.checkin.created"


def test_occurred_at_is_utc():
    env = EventEnvelope(
        event_type="test.event",
        actor=Actor(type="system", id="system"),
        data={},
    )
    assert env.occurred_at.tzinfo == timezone.utc


def test_two_events_have_different_ids():
    actor = Actor(type="user", id="u1")
    e1 = EventEnvelope(event_type="test", actor=actor, data={})
    e2 = EventEnvelope(event_type="test", actor=actor, data={})
    assert e1.event_id != e2.event_id


def test_version_defaults_to_one():
    env = EventEnvelope(
        event_type="content.post.published",
        actor=Actor(type="user", id="u1"),
        data={},
    )
    assert env.version == 1
