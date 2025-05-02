from uuid import UUID

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from core.dependencies import DBSession
from models.orm_models.core import Content
from models.schema.content_schema import CreateContent, ContentSchema
from core import get_response_schema, CustomResponse

# APIRouter with versioning and auth dependency
contents_router = APIRouter(
    prefix="/contents",
    tags=["Contents"],
    responses={
        **get_response_schema(201, "Content successfully created"),
        **get_response_schema(200, ""),
        **get_response_schema(404, "Content item not found"),
        **get_response_schema(422, "Content invalid content"),
        **get_response_schema(409, "Content has conflict with other object"),
    },
)


@contents_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
)
async def create_content(
    request: Request,
    session: AsyncSession = Depends(DBSession),
    data: CreateContent = Depends(),
):
    """Create a new content item"""
    content = await Content.create(
        session=session,
        data=data.model_dump(),
    )
    schema = ContentSchema()
    return CustomResponse(content=schema.dump(content), status_code=201)


@contents_router.get("/")
async def list_contents(
    request: Request,
    session: AsyncSession = Depends(DBSession),
    page: int = 1,
    limit: int = 100,
):
    """List all content items with pagination"""
    query = select(Content)
    if limit:
        query = query.limit(limit)

    if page:
        offset = (page - 1) * limit
        query = query.offset(offset)

    contents = (await session.execute(query)).scalars().all()
    schema = ContentSchema()
    content = schema.dump(contents, many=True)
    return CustomResponse(content=content, status_code=200)


@contents_router.get(
    "/{content_id}",
    status_code=status.HTTP_200_OK,
)
async def get_content(
    request: Request,
    content_id: int,
    session: AsyncSession = Depends(DBSession),
):
    """Get a single content item's info"""
    content = await Content.get(
        session,
        keys={'id': content_id},
        raise_exception=True,
    )
    schema = ContentSchema()
    return CustomResponse(content=schema.dump(content), status_code=200)


@contents_router.put(
    "/{content_id}",
    status_code=status.HTTP_200_OK,
)
async def update_content(
    request: Request,
    content_id: int,
    data: CreateContent = Depends(),
    session: AsyncSession = Depends(DBSession),
):
    """Update a content item"""
    content = await Content.get(
        session,
        keys={'id': content_id},
        raise_exception=True,
    )
    content = await content.update(session, data.model_dump())
    schema = ContentSchema()
    return CustomResponse(content=schema.dump(content), status_code=200)


@contents_router.delete(
    "/{content_id}",
    status_code=status.HTTP_200_OK,
    responses={
        **get_response_schema(
            200,
            "Content successfully deleted",
        )
    },
)
async def delete_content(
    request: Request,
    content_id: int,
    session: AsyncSession = Depends(DBSession),
):
    """Delete a content item"""
    content = await Content.get(
        session,
        keys={'id': content_id},
        raise_exception=True,
    )
    await content.delete(session)
    return CustomResponse(message="")


@contents_router.patch(
    "/{content_id}/publish",
    status_code=status.HTTP_200_OK,
)
async def publish_content(
    request: Request,
    content_id: int,
    session: AsyncSession = Depends(DBSession),
):
    """Publish a content item"""
    content = await Content.get(
        session,
        keys={'id': content_id},
        raise_exception=True,
    )
    content = await content.publish(session)
    schema = ContentSchema()
    return CustomResponse(content=schema.dump(content), status_code=200)


@contents_router.get(
    "/drafts/",
    status_code=status.HTTP_200_OK,
)
async def list_drafts(
    request: Request,
    session: AsyncSession = Depends(DBSession),
    page: int = 1,
    limit: int = 100,
):
    """List all draft content items"""
    query = select(Content).filter_by(is_draft=True)
    if limit:
        query = query.limit(limit)

    if page:
        offset = (page - 1) * limit
        query = query.offset(offset)

    drafts = (await session.execute(query)).scalars().all()
    schema = ContentSchema()
    content = schema.dump(drafts, many=True)
    return CustomResponse(content=content, status_code=200)


@contents_router.post(
    "/{content_id}/revisions/",
    status_code=status.HTTP_201_CREATED,
)
async def save_revision(
    request: Request,
    content_id: int,
    session: AsyncSession = Depends(DBSession),
):
    """Save a revision for a content item"""
    content = await Content.get(
        session,
        keys={'id': content_id},
        raise_exception=True,
    )
    revision = await content.save_revision(session)
    schema = ContentSchema()
    return CustomResponse(content=schema.dump(revision), status_code=201)


@content_router.patch("/{content_id}/publish", status_code=status.HTTP_200_OK)
async def publish_content(content_id: int, request: Request):
    pass


@content_router.get("/drafts/", status_code=status.HTTP_200_OK)
async def get_drafts(request: Request):
    pass


@content_router.post("/{content_id}/revisions/",
                     status_code=status.HTTP_201_CREATED)
async def save_revision(content_id: int, request: Request):
    pass
