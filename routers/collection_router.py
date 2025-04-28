
from fastapi import APIRouter, Depends, Request, status
from fastapi_pagination import Page, Params

from models.schema.collection_schema import (
    CollectionCreate,
    CollectionOut,
    RecordOut,
)

# APIRouter with versioning and auth dependency
collections_router = APIRouter(
    prefix="/v1/collections",
    tags=["Collections"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not Found"}},
)


@collections_router.get("/", response_model=Page[CollectionOut])
async def list_collections(
        request: Request,
        params: Params = Depends(),
):
    pass


@collections_router.post("/", response_model=CollectionOut,
                         status_code=status.HTTP_201_CREATED)
async def create_collection(payload: CollectionCreate):
    """Create a new collection"""
    # TODO: insert into DB
    return CollectionOut(
        id="new-uuid",
        **payload.dict(),
    )


@collections_router.get("/{collection_name}", response_model=CollectionOut)
async def get_collection(collection_name: str):
    """Get a single collection's info"""
    # TODO: fetch from DB
    return CollectionOut(
        id="uuid",
        collection=collection_name,
        hidden=False,
        singleton=False,
    )


@collections_router.patch("/{collection_name}", response_model=CollectionOut)
async def update_collection(collection_name: str, payload: CollectionCreate):
    """Update a collection"""
    # TODO: update DB
    return CollectionOut(
        id="uuid",
        **payload.dict(),
    )


@collections_router.delete("/{collection_name}",
                           status_code=status.HTTP_204_NO_CONTENT)
async def delete_collection(collection_name: str):
    """Delete a collection"""
    # TODO: delete from DB
    return


@collections_router.get("/{collection_name}/records",response_model=Page[RecordOut])
async def list_records(
        collection_name: str,
        params: Params = Depends(),
):
    pass


@collections_router.post("/{collection_name}/records",
                         status_code=status.HTTP_201_CREATED)
async def create_record(collection_name: str, payload: dict):
    """Create a record inside a collection"""
    # TODO: insert into DB
    return {"id": "new-id", "data": payload}


@collections_router.get("/{collection_name}/records/{record_id}",
                        response_model=RecordOut)
async def get_record(collection_name: str, record_id: str):
    pass


@collections_router.patch("/{collection_name}/records/{record_id}")
async def update_record(collection_name: str, record_id: str, payload: dict):
    """Update a specific record inside a collection"""
    # TODO: update DB
    return payload


@collections_router.delete("/{collection_name}/records/{record_id}",
                           status_code=status.HTTP_204_NO_CONTENT)
async def delete_record(collection_name: str, record_id: str):
    """Delete a specific record from a collection"""
    # TODO: delete from DB
    return
