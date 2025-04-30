from fastapi import APIRouter, status, HTTPException, Request

from core.dependencies import DBSession
from models.schema.field_schema import MitreField
from models.orm_models.core import Field
field_router = APIRouter(prefix="/fields", tags=["Fields"])


@field_router.post("/")
async def create_field(request: Request, session: DBSession, data: MitreField):
    field = Field.create(db_session=session, data=data.model_dump())
    return field


# Read all fields
@field_router.get("/")
async def read_fields(request: Request, session: DBSession, skip: int = 0, limit: int = 100):
    fields = await session.execute(Field)
    return fields

# Read a specific field by ID
@field_router.get("/{field_id}")
async def read_field(request: Request, session: DBSession, field_id: int):
    field = db.query(MitreFieldModel).filter(MitreFieldModel.id == field_id).first()
    if field is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Field not found")
    return field

# Update a field (partial update)
@field_router.patch("/{field_id}")
async def update_field(request: Request,  session: DBSession, field_id: int, data: MitreField):
    field = db.query(MitreFieldModel).filter(MitreFieldModel.id == field_id).first()
    if field is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Field not found")
    field_data = data.model_dump(exclude_unset=True)
    for key, value in field_data.items():
        setattr(field, key, value)
    db.add(field)
    db.commit()
    db.refresh(field)
    return field

# Delete a field
@field_router.delete("/{field_id}")
async def delete_field(request: Request, session: DBSession, field_id: int):
    field = db.query(MitreFieldModel).filter(MitreFieldModel.id == field_id).first()
    if field is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Field not found")
    db.delete(field)
    db.commit()
    return field
