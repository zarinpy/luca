from uuid import UUID

from fastapi import APIRouter, status
from sqlalchemy import select

from core import CustomResponse, get_response_schema
from core.dependencies import DBSession
from models.orm_models.core import Collection
from models.schema.collection_schema import (
    CollectionSchema,
    CreateCollection,
)

# APIRouter with versioning and auth dependency
collections_router = APIRouter(
    prefix="/collections",
    tags=["Collections"],
    responses={
        **get_response_schema(
            201,
            "Collection successfully created"),
        **get_response_schema(200, ""),
        **get_response_schema(
            404,
            "Collection item not found",
        ),
        **get_response_schema(
            422,
            "Collection invalid content",
        ),
        **get_response_schema(
            409,
            "Collection has conflict with other object",
        ),
    },
)


@collections_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
)
async def create_collection(

        session: DBSession,
        data: CreateCollection,
) -> None :
    """Create a new collection"""
    collection = await Collection.create(
        session=session,
        data=data.model_dump(),
    )
    schema = CollectionSchema()
    return CustomResponse(content=schema.dump(collection), status_code=201)


@collections_router.get("/")
async def list_collections(

        session: DBSession,
        page: int = 1,
        limit: int = 100,
) -> None :
    query = select(Collection)
    if limit:
        query = query.limit(limit)

    if page:
        offset = (page - 1) * limit
        query = query.offset(offset)

    fields = (await session.execute(query)).scalars().all()
    schema = CollectionSchema()
    content = schema.dump(fields, many=True)
    return CustomResponse(content=content, status_code=200)


@collections_router.get(
    "/{collection_id}",
    status_code=status.HTTP_200_OK,
)
async def get_collection(

        session: DBSession,
        collection_id: UUID,
) -> None :
    """Get a single collection's info"""
    collection = await Collection.get(
        session,
        keys={"id": collection_id},
        raise_exception=True,
    )
    schema = CollectionSchema()
    return CustomResponse(content=schema.dump(collection), status_code=200)


@collections_router.patch(
    "/{collection_id}",
    status_code=status.HTTP_200_OK,
)
async def update_collection(

        session: DBSession,
        collection_id: UUID,
        data: CreateCollection,
) -> None :
    """Update a collection"""
    collection = await Collection.get(
        session,
        keys={"id": collection_id},
        raise_exception=True,
    )
    collection = await collection.update(session, data)
    schema = CollectionSchema()
    return CustomResponse(content=schema.dump(collection), status_code=200)


@collections_router.delete(
    "/{collection_id}",
    status_code=status.HTTP_200_OK,
    responses={
        **get_response_schema(
            200,
            "Collection successfully deleted",
        ),
    },
)
async def delete_collection(

        session: DBSession,
        collection_id: UUID,
) -> None :
    """Delete a collection"""
    collection = await Collection.get(
        session,
        keys={"id": collection_id},
        raise_exception=True,
    )
    await collection.delete(session)
    return CustomResponse(message="")
