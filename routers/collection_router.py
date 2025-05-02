from uuid import UUID

from fastapi import APIRouter, Depends, Request, status
from fastapi_pagination import Params
from models.orm_models.core import Collection
from sqlalchemy import select
from core.dependencies import DBSession
from models.schema.collection_schema import (
    CreateCollection,
    CollectionSchema,
)
from core import get_response_schema, CustomResponse

# APIRouter with versioning and auth dependency
collections_router = APIRouter(
    prefix="/collections",
    tags=["Collections"],
    responses={
        **get_response_schema(201, "Collection successfully created"),
        **get_response_schema(200, ""),
        **get_response_schema(404, "Collection item not found"),
        **get_response_schema(422, "Collection invalid content"),
        **get_response_schema(409, "Collection has conflict with other object"),
    },
)


@collections_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
)
async def create_collection(
        request: Request,
        session: DBSession,
        data: CreateCollection,
):
    """Create a new collection"""
    collection = await Collection.create(
        session=session,
        data=data.model_dump(),
    )
    schema = CollectionSchema()
    return CustomResponse(content=schema.dump(collection), status_code=201)


@collections_router.get("/")
async def list_collections(
        request: Request,
        session: DBSession,
        page: int = 1,
        limit: int = 100
):
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
        request: Request,
        session: DBSession,
        collection_id: UUID,
):
    """Get a single collection's info"""
    collection = await Collection.get(
        session,
        keys={'id': collection_id},
        raise_exception=True
    )
    schema = CollectionSchema()
    return CustomResponse(content=schema.dump(collection), status_code=200)


@collections_router.patch(
    "/{collection_id}",
    status_code=status.HTTP_200_OK,
)
async def update_collection(
        request: Request,
        session: DBSession,
        collection_id: UUID,
        data: CreateCollection,
):
    """Update a collection"""
    collection = await Collection.get(
        session,
        keys={'id': collection_id},
        raise_exception=True
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
        )
    }
)
async def delete_collection(
        request: Request,
        session: DBSession,
        collection_id: UUID
):
    """Delete a collection"""
    collection = await Collection.get(
        session,
        keys={'id': collection_id},
        raise_exception=True
    )
    await collection.delete(session)
    return CustomResponse(message="")


@collections_router.get("/{collection_id}/records")
async def list_records(
        request: Request,
        session: DBSession,
        collection_id: UUID,
        params: Params = Depends(),
):
    pass


@collections_router.post(
    "/{collection_id}/records",
    status_code=status.HTTP_201_CREATED,
)
async def create_record(
        request: Request,
        session: DBSession,
        collection_id: UUID,
        data: dict,
):
    """Create a record inside a collection"""
    # TODO: insert into DB
    return {"id": "new-id", "data": ""}


@collections_router.get(
    "/{collection_id}/records/{record_id}",
    status_code=status.HTTP_200_OK,
)
async def get_record(
        request: Request,
        session: DBSession,
        record_id: UUID,
        collection_id: UUID,
):
    pass


@collections_router.patch("/{collection_id}/records/{record_id}")
async def update_record(
        request: Request,
        session: DBSession,
        collection_id: UUID,
        record_id: UUID,
        data: dict,
):
    """Update a specific record inside a collection"""
    # TODO: update DB
    return data


@collections_router.delete(
    "/{collection_id}/records/{record_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_record(
        request: Request,
        session: DBSession,
        collection_: UUID,
        record_id: UUID,
):
    """Delete a specific record from a collection"""
    # TODO: delete from DB
    return
