from unittest.mock import MagicMock

from polymath_llm.client import LLMClient
from polymath_llm.models import CompletionRequest, Message


def _client() -> LLMClient:
    return LLMClient(redis=MagicMock())


def _req(**kwargs) -> CompletionRequest:
    defaults: dict = {
        "model": "claude-sonnet-4-6",
        "messages": [Message(role="user", content="hello")],
    }
    defaults.update(kwargs)
    return CompletionRequest(**defaults)


def test_same_request_same_key():
    c = _client()
    r = _req()
    assert c._cache_key(r) == c._cache_key(r)


def test_different_model_different_key():
    c = _client()
    assert c._cache_key(_req(model="gpt-4o")) != c._cache_key(_req(model="claude-sonnet-4-6"))


def test_different_content_different_key():
    c = _client()
    r1 = _req(messages=[Message(role="user", content="hello")])
    r2 = _req(messages=[Message(role="user", content="world")])
    assert c._cache_key(r1) != c._cache_key(r2)


def test_key_has_prefix():
    c = _client()
    assert c._cache_key(_req()).startswith("llm:cache:")


def test_key_is_deterministic():
    c = _client()
    r = _req()
    assert len({c._cache_key(r) for _ in range(5)}) == 1
