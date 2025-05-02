from typing import Any, Dict, Optional

from pydantic import BaseModel, Field
from marshmallow import Schema, fields
from models.orm_models.core import Collection


class CollectionSchema(Schema):
    """Output schema for a collection.
    """

    id = fields.UUID()
    collection = fields.Str()
    hidden = fields.Bool()
    singleton = fields.Bool()

    class Meta:
        model = Collection


class CreateCollection(BaseModel):
    """
    Pydantic model for the mitre_collections table, representing metadata about each collection.
    """
    collection: str = Field(
        ...,
        alias="name",
        description="Unique collection name/key",
        min_length=1,
    )
    hidden: bool = Field(
        default=False,
        description="Whether hidden in the UI",
    )
    singleton: bool = Field(
        default=False,
        description="True if only one record allowed",
    )
    icon: Optional[Dict[str, Any]] = Field(
        default={},
        description="UI icon metadata",
    )
    note: Optional[Dict[str, Any]] = Field(
        default={},
        description="Arbitrary notes/metadata",
    )
    translations: Optional[Dict[str, Any]] = Field(
        default={},
        description="Multilanguage labels",
    )

    class Config:
        extra = "forbid"
