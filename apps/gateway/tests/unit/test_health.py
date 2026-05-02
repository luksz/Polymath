def test_liveness(client):
    response = client.get("/healthz")
    assert response.status_code == 200


def test_readiness(client):
    response = client.get("/readyz")
    assert response.status_code == 200


def test_version(client):
    response = client.get("/version")
    assert response.status_code == 200
    assert response.json()["service"] == "gateway"
