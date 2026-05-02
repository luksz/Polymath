from typing import Any

import httpx
import structlog
from fastapi import Request
from polymath_core.errors import UnauthorizedError

logger = structlog.get_logger()

# Verify Clerk JWT by fetching the JWKS and validating the token.
# In dev (no CLERK_SECRET_KEY set), allow requests with X-Dev-User-Id header for testing.


class ClerkAuth:
    def __init__(self, secret_key: str) -> None:
        self._secret_key = secret_key
        self._jwks_cache: dict[str, Any] | None = None

    async def verify_request(self, request: Request) -> str | None:
        """
        Verify Clerk session token. Returns user_id or None for unauthenticated.
        Raises UnauthorizedError if token is present but invalid.
        """
        # Dev bypass: if no clerk key configured, trust X-Dev-User-Id
        if not self._secret_key:
            return request.headers.get("X-Dev-User-Id")

        auth_header = request.headers.get("Authorization", "")
        session_cookie = request.cookies.get("__session", "")
        token = ""

        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
        elif session_cookie:
            token = session_cookie

        if not token:
            return None

        try:
            import jwt as pyjwt

            # Fetch JWKS from Clerk
            if self._jwks_cache is None:
                async with httpx.AsyncClient() as client:
                    resp = await client.get("https://api.clerk.com/v1/jwks", timeout=5.0)
                    self._jwks_cache = resp.json()

            # Decode and verify
            header = pyjwt.get_unverified_header(token)
            key_id = header.get("kid")

            # Find matching key
            keys = self._jwks_cache.get("keys", [])
            matching_key = next((k for k in keys if k.get("kid") == key_id), None)
            if not matching_key:
                raise UnauthorizedError("Invalid token key")

            public_key = pyjwt.algorithms.RSAAlgorithm.from_jwk(matching_key)
            payload = pyjwt.decode(
                token,
                public_key,
                algorithms=["RS256"],
                options={"verify_exp": True},
            )
            return payload.get("sub")
        except UnauthorizedError:
            raise
        except Exception as e:
            logger.warning("clerk_jwt_verification_failed", error=str(e))
            raise UnauthorizedError("Invalid or expired session token")
