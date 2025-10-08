from __future__ import annotations

from typing import Any

from marshmallow import Schema, fields
from pydantic import BaseModel, Field

from models.orm_models.core import Collection


class CollectionSchema(Schema):
    """Output schema for a collection."""

    id = fields.UUID()
    collection = fields.Str()
    hidden = fields.Bool()
    singleton = fields.Bool()

    class Meta:
        model = Collection


class CreateCollection(BaseModel):

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
    icon: dict[str, Any] | None = Field(
        default={},
        description="UI icon metadata",
    )
    note: dict[str, Any] | None = Field(
        default={},
        description="Arbitrary notes/metadata",
    )
    translations: dict[str, Any] | None = Field(
        default={},
        description="Multilanguage labels",
    )

    class Config:
        extra = "forbid"
