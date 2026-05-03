import httpx
import structlog
from polymath_core.errors import NotFoundError, PolymathError

logger = structlog.get_logger()


class ServiceClient:
    """Base async HTTP client for internal service calls."""

    def __init__(self, base_url: str, service_secret: str, timeout: float = 5.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._service_secret = service_secret
        self._timeout = timeout

    def _headers(self, user_id: str | None, request_id: str = "") -> dict[str, str]:
        headers: dict[str, str] = {
            "X-Polymath-Service-Token": "dev-token",  # TODO: HMAC in Phase 1+
            "X-Request-ID": request_id,
        }
        if user_id:
            headers["X-Polymath-User-Id"] = user_id
        return headers

    async def get(self, path: str, user_id: str | None = None, **kwargs) -> dict:
        async with httpx.AsyncClient(base_url=self._base_url, timeout=self._timeout) as client:
            resp = await client.get(path, headers=self._headers(user_id), **kwargs)
            return self._handle(resp)

    async def post(self, path: str, user_id: str | None = None, **kwargs) -> dict:
        async with httpx.AsyncClient(base_url=self._base_url, timeout=self._timeout) as client:
            resp = await client.post(path, headers=self._headers(user_id), **kwargs)
            return self._handle(resp)

    async def put(self, path: str, user_id: str | None = None, **kwargs) -> dict:
        async with httpx.AsyncClient(base_url=self._base_url, timeout=self._timeout) as client:
            resp = await client.put(path, headers=self._headers(user_id), **kwargs)
            return self._handle(resp)

    async def delete(self, path: str, user_id: str | None = None, **kwargs) -> None:
        async with httpx.AsyncClient(base_url=self._base_url, timeout=self._timeout) as client:
            resp = await client.delete(path, headers=self._headers(user_id), **kwargs)
            if resp.status_code >= 400:
                raise PolymathError(f"Upstream error {resp.status_code}: {resp.text[:200]}")

    def _handle(self, resp: httpx.Response) -> dict:
        if resp.status_code == 404:
            raise NotFoundError(resp.text)
        if resp.status_code >= 400:
            raise PolymathError(f"Upstream error {resp.status_code}: {resp.text[:200]}")
        return resp.json()
