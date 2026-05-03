import pytest
from fastapi.testclient import TestClient

from notes_svc.main import app


@pytest.fixture
def client() -> TestClient:
    with TestClient(app) as c:
        yield c
