from fastapi import APIRouter, Depends

from ...config import GatewaySettings
from ...deps import get_settings, require_user
from ...infra.clients.digest_client import DigestClient

router = APIRouter()


def get_digest_client(settings: GatewaySettings = Depends(get_settings)) -> DigestClient:
    return DigestClient(
        base_url=settings.digest_svc_url,
        service_secret=settings.polymath_service_secret,
        timeout=30.0,
    )


@router.get("")
async def list_digests(
    user_id: str = Depends(require_user),
    digest: DigestClient = Depends(get_digest_client),
) -> list:
    return await digest.list_digests(user_id=user_id)


@router.get("/today")
async def get_today(
    user_id: str = Depends(require_user),
    digest: DigestClient = Depends(get_digest_client),
) -> dict:
    return await digest.get_today(user_id=user_id)


@router.get("/{date}")
async def get_by_date(
    date: str,
    user_id: str = Depends(require_user),
    digest: DigestClient = Depends(get_digest_client),
) -> dict:
    return await digest.get_by_date(user_id=user_id, date=date)


@router.post("/run", status_code=202)
async def trigger_run(
    user_id: str = Depends(require_user),
    digest: DigestClient = Depends(get_digest_client),
) -> dict:
    return await digest.trigger_run(user_id=user_id)
