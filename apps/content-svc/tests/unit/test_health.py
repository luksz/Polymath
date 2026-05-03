def test_liveness(client):
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_version_shape(client):
    response = client.get("/version")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "content-svc"
    assert "version" in data
