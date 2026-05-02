from fastapi import APIRouter

from .v1.routes_complete import router as complete_router
from .v1.routes_embed import router as embed_router
from .v1.routes_prompts import router as prompts_router
from .v1.routes_usage import router as usage_router

router = APIRouter()
router.include_router(complete_router, prefix="/complete", tags=["completions"])
router.include_router(prompts_router, prefix="/prompts", tags=["prompts"])
router.include_router(embed_router, prefix="/embed", tags=["embeddings"])
router.include_router(usage_router, prefix="/usage", tags=["usage"])
