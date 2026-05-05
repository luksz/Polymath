import asyncio
from contextlib import asynccontextmanager

import structlog
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from polymath_core.logging import configure_logging
from polymath_core.middleware import RequestIDMiddleware
from polymath_core.otel import configure_otel

from .config import JobsSvcSettings
from .jobs.digest import run_daily_digest

logger = structlog.get_logger()
settings = JobsSvcSettings()
scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging(settings.log_level, settings.service_name)
    configure_otel(settings.service_name, settings.otel_exporter_otlp_endpoint)

    scheduler.add_job(
        run_daily_digest,
        trigger=CronTrigger(hour=settings.digest_cron_hour, minute=settings.digest_cron_minute, timezone="UTC"),
        kwargs={"digest_svc_url": settings.digest_svc_url},
        id="daily_digest",
        replace_existing=True,
        misfire_grace_time=3600,
    )
    scheduler.start()
    logger.info("scheduler_started", jobs=[j.id for j in scheduler.get_jobs()])
    yield
    scheduler.shutdown(wait=False)


app = FastAPI(title="Polymath Jobs Service", version="0.1.0", lifespan=lifespan)
app.add_middleware(RequestIDMiddleware)


@app.get("/healthz")
async def healthz() -> dict:
    return {"status": "ok"}


@app.get("/version")
async def version() -> dict:
    return {"service": "jobs-svc", "version": "0.1.0"}


@app.get("/jobs")
async def list_jobs() -> list:
    return [
        {
            "id": job.id,
            "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
        }
        for job in scheduler.get_jobs()
    ]


@app.post("/jobs/digest/trigger", status_code=202)
async def trigger_digest() -> dict:
    asyncio.create_task(run_daily_digest(settings.digest_svc_url))
    return {"status": "triggered"}
