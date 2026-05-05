import httpx
import structlog

logger = structlog.get_logger()


async def run_daily_digest(digest_svc_url: str) -> None:
    logger.info("daily_digest_job_started", url=digest_svc_url)
    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            resp = await client.post(
                f"{digest_svc_url.rstrip('/')}/v1/digests/run",
                headers={"X-Polymath-User-Id": "jobs-svc"},
            )
            resp.raise_for_status()
        logger.info("daily_digest_job_triggered")
    except Exception as e:
        logger.error("daily_digest_job_failed", error=str(e))
