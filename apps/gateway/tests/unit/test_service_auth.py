from gateway.service_auth import generate_service_token, verify_service_token


def test_valid_token_verifies():
    body = b'{"test": "data"}'
    secret = "test-secret-abc"
    token = generate_service_token(body, secret)
    assert verify_service_token(token, body, secret)


def test_wrong_secret_fails():
    body = b'{"test": "data"}'
    token = generate_service_token(body, "secret-a")
    assert not verify_service_token(token, body, "secret-b")


def test_tampered_body_fails():
    body = b'{"test": "data"}'
    token = generate_service_token(body, "secret")
    assert not verify_service_token(token, b'{"test": "tampered"}', "secret")
