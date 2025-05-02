from uuid import UUID

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from core.dependencies import DBSession
from models.orm_models.core import Field
from models.schema.field_schema import CreateField, FieldSchema
from core import get_response_schema, CustomResponse

# APIRouter with versioning and auth dependency
fields_router = APIRouter(
    prefix="/fields",
    tags=["Fields"],
    responses={
        **get_response_schema(201, "Field successfully created"),
        **get_response_schema(200, ""),
        **get_response_schema(404, "Field item not found"),
        **get_response_schema(422, "Field invalid content"),
        **get_response_schema(409, "Field has conflict with other object"),
    },
)


@fields_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
)
async def create_field(
    request: Request,
    session: AsyncSession = Depends(DBSession),
    data: CreateField = Depends(),
):
    """Create a new field"""
    field = await Field.create(
        session=session,
        data=data.model_dump(),
    )
    schema = FieldSchema()
    return CustomResponse(content=schema.dump(field), status_code=201)


@fields_router.get("/")
async def list_fields(
    request: Request,
    session: AsyncSession = Depends(DBSession),
    page: int = 1,
    limit: int = 100,
):
    """List all fields with pagination"""
    query = select(Field)
    if limit:
        query = query.limit(limit)

    if page:
        offset = (page - 1) * limit
        query = query.offset(offset)

    fields = (await session.execute(query)).scalars().all()
    schema = FieldSchema()
    content = schema.dump(fields, many=True)
    return CustomResponse(content=content, status_code=200)


@fields_router.get(
    "/{field_id}",
    status_code=status.HTTP_200_OK,
)
async def get_field(
    request: Request,
    field_id: int,
    session: AsyncSession = Depends(DBSession),
):
    """Get a single field's info"""
    field = await Field.get(
        session,
        keys={'id': field_id},
        raise_exception=True,
    )
    schema = FieldSchema()
    return CustomResponse(content=schema.dump(field), status_code=200)


@fields_router.patch(
    "/{field_id}",
    status_code=status.HTTP_200_OK,
)
async def update_field(
    request: Request,
    field_id: int,
    data: CreateField = Depends(),
    session: AsyncSession = Depends(DBSession),
):
    """Update a field"""
    field = await Field.get(
        session,
        keys={'id': field_id},
        raise_exception=True,
    )
    field = await field.update(session, data.model_dump())
    schema = FieldSchema()
    return CustomResponse(content=schema.dump(field), status_code=200)


@fields_router.delete(
    "/{field_id}",
    status_code=status.HTTP_200_OK,
    responses={
        **get_response_schema(
            200,
            "Field successfully deleted",
        )
    },
)
async def delete_field(
    request: Request,
    field_id: int,
    session: AsyncSession = Depends(DBSession),
):
    """Delete a field"""
    field = await Field.get(
        session,
        keys={'id': field_id},
        raise_exception=True,
    )
    await field.delete(session)
    return CustomResponse(message="")