import pytest
from fastapi.testclient import TestClient

from llm_gateway.main import app


@pytest.fixture
def client() -> TestClient:
    with TestClient(app) as c:
        yield c
