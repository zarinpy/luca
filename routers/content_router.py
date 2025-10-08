
from fastapi import APIRouter, Request, status
from sqlalchemy import select

from core import CustomResponse, get_response_schema
from core.dependencies import DBSession
from models.orm_models.core import Content
from models.schema.content_schema import ContentSchema, CreateContent

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
    session: DBSession,
    data: CreateContent,
) -> None :
    """Create a new content item"""
    content = await Content.create(
        session=session,
        data=data.model_dump(),
    )
    schema = ContentSchema()
    return CustomResponse(content=schema.dump(content), status_code=201)


@contents_router.get("/")
async def list_contents(
    session: DBSession,
    page: int = 1,
    limit: int = 100,
) -> None :
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
async def get_content(content_id: int, session: DBSession) -> None :
    """Get a single content item's info"""
    content = await Content.get(
        session,
        keys={"id": content_id},
        raise_exception=True,
    )
    schema = ContentSchema()
    return CustomResponse(content=schema.dump(content), status_code=200)


@contents_router.put(
    "/{content_id}",
    status_code=status.HTTP_200_OK,
)
async def update_content(
    session: DBSession,
    content_id: int,
    data: CreateContent,
) -> None :
    """Update a content item"""
    content = await Content.get(
        session,
        keys={"id": content_id},
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
        ),
    },
)
async def delete_content(content_id: int, session: DBSession) -> None :
    """Delete a content item"""
    content = await Content.get(
        session,
        keys={"id": content_id},
        raise_exception=True,
    )
    await content.delete(session)
    return CustomResponse(message="")


@contents_router.patch(
    "/{content_id}/publish",
    status_code=status.HTTP_200_OK,
)
async def publish_content(content_id: int, session: DBSession) -> None :
    """Publish a content item"""
    content = await Content.get(
        session,
        keys={"id": content_id},
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
    session: DBSession,
    page: int = 1,
    limit: int = 100,
) -> None :
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
async def save_revision(content_id: int, session: DBSession) -> None :
    """Save a revision for a content item"""
    content = await Content.get(
        session,
        keys={"id": content_id},
        raise_exception=True,
    )
    revision = await content.save_revision(session)
    schema = ContentSchema()
    return CustomResponse(content=schema.dump(revision), status_code=201)


@contents_router.patch("/{content_id}/publish", status_code=status.HTTP_200_OK)
async def publish_content_logic(content_id: int, request: Request) -> None :
    pass


@contents_router.get("/drafts/", status_code=status.HTTP_200_OK)
async def get_drafts_logic(request: Request) -> None :
    pass


@contents_router.post("/{content_id}/revisions/",
                     status_code=status.HTTP_201_CREATED)
async def save_revision_logic(content_id: int, request: Request) -> None :
    pass
