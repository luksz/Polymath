from polymath_db.base import Base, TimestampMixin, UUIDMixin
from sqlalchemy.orm import DeclarativeBase


def test_uuid_mixin_has_id():
    assert hasattr(UUIDMixin, "id")


def test_timestamp_mixin_has_created_at():
    assert hasattr(TimestampMixin, "created_at")


def test_timestamp_mixin_has_updated_at():
    assert hasattr(TimestampMixin, "updated_at")


def test_base_is_declarative_base():
    assert issubclass(Base, DeclarativeBase)
