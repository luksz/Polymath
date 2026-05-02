from fastapi import APIRouter
from .v1.routes_health import health_router
from .v1.routes_llm import router as llm_router

router = APIRouter()
router.include_router(llm_router, prefix="/v1/llm", tags=["llm"])
