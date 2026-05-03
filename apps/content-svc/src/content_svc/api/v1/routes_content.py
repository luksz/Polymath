import uuid
from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, Header, Query
from fastapi.responses import JSONResponse, Response
from feedgen.feed import FeedGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from polymath_core.errors import UnauthorizedError

from ...deps import get_db
from ...domain.services import PostService, ReadingLogService
from .schemas import (
    PostCreate,
    PostDetailResponse,
    PostResponse,
    PostUpdate,
    ReadingLogCreate,
    ReadingLogResponse,
)

logger = structlog.get_logger()

_post_service = PostService()
_reading_log_service = ReadingLogService()

posts_router = APIRouter(prefix="/v1/posts", tags=["posts"])
reading_log_router = APIRouter(prefix="/v1/reading-log", tags=["reading-log"])
feeds_router = APIRouter(prefix="/v1", tags=["feeds"])


def _require_user_id(
    x_polymath_user_id: Annotated[str | None, Header(alias="X-Polymath-User-Id")] = None,
) -> str:
    if not x_polymath_user_id:
        raise UnauthorizedError("X-Polymath-User-Id header is required")
    return x_polymath_user_id


# ---------------------------------------------------------------------------
# Posts
# ---------------------------------------------------------------------------


@posts_router.get("/", response_model=list[PostResponse])
async def list_posts(
    kind: str | None = Query(default=None),
    tag: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> list[PostResponse]:
    posts = await _post_service.list_posts(db, kind=kind, tag=tag, limit=limit, offset=offset)
    return [PostResponse.model_validate(p) for p in posts]


@posts_router.get("/{slug}", response_model=PostDetailResponse)
async def get_post(
    slug: str,
    db: AsyncSession = Depends(get_db),
) -> PostDetailResponse:
    post = await _post_service.get_post(db, slug)
    return PostDetailResponse.model_validate(post)


@posts_router.post("/", response_model=PostDetailResponse, status_code=201)
async def create_post(
    payload: PostCreate,
    user_id: str = Depends(_require_user_id),
    db: AsyncSession = Depends(get_db),
) -> PostDetailResponse:
    post = await _post_service.create_post(
        db,
        slug=payload.slug,
        kind=payload.kind,
        title=payload.title,
        body_mdx=payload.body_mdx,
        summary=payload.summary,
        tags=payload.tags,
        cover_image_url=payload.cover_image_url,
    )
    return PostDetailResponse.model_validate(post)


@posts_router.put("/{post_id}", response_model=PostDetailResponse)
async def update_post(
    post_id: uuid.UUID,
    payload: PostUpdate,
    user_id: str = Depends(_require_user_id),
    db: AsyncSession = Depends(get_db),
) -> PostDetailResponse:
    updates = payload.model_dump(exclude_none=True)
    post = await _post_service.update_post(db, post_id, **updates)
    return PostDetailResponse.model_validate(post)


@posts_router.post("/{post_id}/publish", response_model=PostDetailResponse)
async def publish_post(
    post_id: uuid.UUID,
    user_id: str = Depends(_require_user_id),
    db: AsyncSession = Depends(get_db),
) -> PostDetailResponse:
    post = await _post_service.publish_post(db, post_id)
    return PostDetailResponse.model_validate(post)


# ---------------------------------------------------------------------------
# Reading log
# ---------------------------------------------------------------------------


@reading_log_router.get("/", response_model=list[ReadingLogResponse])
async def list_reading_log(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> list[ReadingLogResponse]:
    entries = await _reading_log_service.list_entries(db, limit=limit, offset=offset)
    return [ReadingLogResponse.model_validate(e) for e in entries]


@reading_log_router.post("/", response_model=ReadingLogResponse, status_code=201)
async def add_reading_log_entry(
    payload: ReadingLogCreate,
    user_id: str = Depends(_require_user_id),
    db: AsyncSession = Depends(get_db),
) -> ReadingLogResponse:
    entry = await _reading_log_service.add_entry(
        db,
        user_id=user_id,
        title=payload.title,
        url=payload.url,
        source=payload.source,
        finished_on=payload.finished_on,
        rating=payload.rating,
        notes_md=payload.notes_md,
        tags=payload.tags,
    )
    return ReadingLogResponse.model_validate(entry)


# ---------------------------------------------------------------------------
# Feeds
# ---------------------------------------------------------------------------


@feeds_router.get("/feed.rss")
async def rss_feed(db: AsyncSession = Depends(get_db)) -> Response:
    posts = await _post_service.list_posts(db, limit=20, offset=0)

    fg = FeedGenerator()
    fg.id("https://polymath.dev/blog")
    fg.title("Polymath Blog")
    fg.link(href="https://polymath.dev/blog", rel="alternate")
    fg.link(href="https://polymath.dev/v1/feed.rss", rel="self")
    fg.description("Latest posts from Polymath")
    fg.language("en")

    for post in posts:
        fe = fg.add_entry()
        fe.id(f"https://polymath.dev/blog/{post.slug}")
        fe.title(post.title)
        fe.link(href=f"https://polymath.dev/blog/{post.slug}")
        if post.summary:
            fe.description(post.summary)
        if post.published_at:
            fe.published(post.published_at)
            fe.updated(post.updated_at)

    rss_str = fg.rss_str(pretty=True)
    return Response(content=rss_str, media_type="application/rss+xml")


@feeds_router.get("/feed.json")
async def json_feed(db: AsyncSession = Depends(get_db)) -> JSONResponse:
    posts = await _post_service.list_posts(db, limit=20, offset=0)

    items = []
    for post in posts:
        item = {
            "id": f"https://polymath.dev/blog/{post.slug}",
            "url": f"https://polymath.dev/blog/{post.slug}",
            "title": post.title,
            "content_html": post.body_mdx,
            "summary": post.summary,
            "tags": post.tags,
        }
        if post.published_at:
            item["date_published"] = post.published_at.isoformat()
            item["date_modified"] = post.updated_at.isoformat()
        if post.cover_image_url:
            item["image"] = post.cover_image_url
        items.append(item)

    feed = {
        "version": "https://jsonfeed.org/version/1.1",
        "title": "Polymath Blog",
        "home_page_url": "https://polymath.dev/blog",
        "feed_url": "https://polymath.dev/v1/feed.json",
        "description": "Latest posts from Polymath",
        "language": "en",
        "items": items,
    }
    return JSONResponse(content=feed)
