from fastapi import APIRouter
from .v1.routes_health import health_router
from .v1.routes_llm import router as llm_router
from .v1.routes_notes import router as notes_router
from .v1.routes_habits import router as habits_router, todos_router
from .v1.routes_content import router as content_router
from .v1.routes_digest import router as digest_router

router = APIRouter()
router.include_router(llm_router, prefix="/v1/llm", tags=["llm"])
router.include_router(notes_router, prefix="/v1/notes", tags=["notes"])
router.include_router(habits_router, prefix="/v1/habits", tags=["habits"])
router.include_router(todos_router, prefix="/v1/todos", tags=["todos"])
router.include_router(content_router, prefix="/v1/content", tags=["content"])
router.include_router(digest_router, prefix="/v1/digests", tags=["digest"])
