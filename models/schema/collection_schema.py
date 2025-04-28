from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# Pydantic schemas
class FieldDefinition(BaseModel):
    field: str
    type: str
    required: bool = False
    interface: Optional[dict]
    options: Optional[dict]


class CollectionOut(BaseModel):
    """Output schema for a collection.
    """

    id: UUID
    collection: str
    hidden: bool
    singleton: bool


class CollectionCreate(BaseModel):
    """Input schema for creating or updating a collection.
    """

    collection: str = Field(
        description=(
            "Unique collection name/key using "
            "lowercase letters, numbers, and underscores"
        ),
    )
    hidden: bool = Field(
        False,
        description="Whether the collection is hidden in the UI",
    )
    singleton: bool = Field(
        False,
        description="True if only one record allowed in this collection",
    )


# Pydantic Models for Records
class RecordOut(BaseModel):
    """Output schema for a record within a collection.
    """

    id: UUID
    data: Dict[str, Any]


class RecordCreate(BaseModel):
    """Input schema for creating or updating a record.
    Accepts arbitrary JSON matching collection's fields.
    """

    data: Dict[str, Any]
