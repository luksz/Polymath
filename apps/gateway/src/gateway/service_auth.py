import hashlib
import hmac
import time


def generate_service_token(body: bytes, secret: str) -> str:
    """Generate HMAC-SHA256 token: sha256(body + timestamp, secret)."""
    timestamp = str(int(time.time()))
    message = body + timestamp.encode()
    sig = hmac.new(secret.encode(), message, hashlib.sha256).hexdigest()
    return f"{timestamp}.{sig}"


def verify_service_token(token: str, body: bytes, secret: str, max_age: int = 30) -> bool:
    """Verify token freshness (within max_age seconds) and HMAC signature."""
    try:
        timestamp_str, sig = token.split(".", 1)
        timestamp = int(timestamp_str)
        if abs(time.time() - timestamp) > max_age:
            return False
        message = body + timestamp_str.encode()
        expected = hmac.new(secret.encode(), message, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, sig)
    except Exception:
        return False
