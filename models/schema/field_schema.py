from __future__ import annotations

import uuid
from typing import ClassVar, Literal

from marshmallow import Schema, fields
from pydantic import BaseModel, Field

from models.orm_models.core import Field as FieldModel

__all__ = ["CreateField", "FieldSchema"]


class SchemaDefinition(BaseModel):
    type: Literal[
        "string", "integer", "number", "boolean",
        "array", "object", "date", "datetime",
    ] = Field(..., description="Data type of the field")
    required: bool | None = Field(
        default=False,
        description="Indicates if the field is required",
    )
    default: str | int | float | bool | list | dict = Field(
        None,
        description="Default value for the field",
    )
    enum: list[str | int] | None = Field(
        None,
        description="list of allowed values",
    )
    min_length: int | None = Field(
        None,
        description="Minimum length for string fields",
    )
    max_length: int | None = Field(
        None,
        description="Maximum length for string fields",
    )
    minimum: float | None = Field(
        None,
        description="Minimum value for numeric fields",
    )
    maximum: float | None = Field(
        None,
        description="Maximum value for numeric fields",
    )
    pattern: str | None = Field(
        None,
        description="Regex pattern for string fields",
    )
    items: SchemaDefinition | None = Field(
        None,
        description="Schema definition for items in array fields",
    )

    class Config:
        extra = "forbid"


class InterfaceSettings(BaseModel):
    widget: str| None = Field(
        None,
        description="Type of UI widget (e.g., 'text', 'select', 'checkbox')",
    )
    label: str| None = Field(
        None,
        description="Label displayed for the field",
    )
    placeholder: str| None = Field(
        None,
        description="Placeholder text for the field",
    )
    help_text: str | None = Field(
        None,
        description="Help text or tooltip for the field",
    )
    readonly: bool | None = Field(
        default=False,
        description="Indicates if the field is read-only",
    )
    hidden: bool | None = Field(
        default=False,
        description="Indicates if the field is hidden in the UI",
    )
    order: int | None = Field(
        None,
        description="Order of the field in the UI",
    )
    css_class: str | None = Field(
        None,
        description="CSS class for styling the field",
    )
    width: str | None = Field(
        None,
        description="Width of the field in the UI (e.g., '50%')",
    )
    icon: str | None = Field(
        None,
        description="Icon associated with the field",
    )

    class Config:
        extra = "forbid"


class AdditionalOptions(BaseModel):
    searchable: bool | None = Field(
        default=False, description="Indicates if the field is searchable",
    )
    sortable: bool | None = Field(
        default=False, description="Indicates if the field is sortable",
    )
    unique: bool | None = Field(
        default=False,
        description="Indicates if the field value must be unique",
    )
    index: bool | None = Field(
        default=False,
        description="Indicates if the field should be indexed in the database",
    )
    default_sort: bool | None = Field(
        default=False,
        description="Indicates if the field is used for default sorting",
    )
    filterable: bool | None = Field(
        default=False,
        description="Indicates if the field can be used for filtering",
    )
    group: str | None = Field(
        None, description="Group name for organizing fields in the UI",
    )
    dependencies: list[str] | None = Field(
        None, description="list of field names this field depends on",
    )

    class Config:
        extra = "forbid"


class CreateField(BaseModel):
    collection: uuid.UUID = Field(
        ...,
        description="CreateCollection this field belongs to",
    )
    field: str = Field(..., description="Name of the field")
    type: str = Field(..., description="Data type of the field")
    schema: SchemaDefinition | None = Field(
        None, description="Schema definition for the field",
    )
    interface: InterfaceSettings | None = Field(
        None, description="UI settings for the field",
    )
    options: AdditionalOptions | None= Field(
        None, description="Additional options for the field",
    )

    class Config:
        extra = "forbid"
        json_schema_extra: ClassVar[dict] = {
            # Use a fixed UUID instead of uuid4() for class-level constancy
            "collection_id": uuid.UUID("12345678-1234-5678-9abc-123456789abc"),
            "field": "username",
            "type": "string",
            "schema": {
                "type": "string",
                "required": True,
                "default": "guest_user",
                "enum": ["guest_user", "admin_user", "regular_user"],
                "min_length": 5,
                "max_length": 20,
                "pattern": "^[a-zA-Z0-9_]+$",
            },
            "interface": {
                "widget": "text",
                "label": "Username",
                "placeholder": "Enter your username",
                "help_text": (
                    "Username must be 5-20 characters long and can include"
                    " letters, numbers, and underscores."
                ),
                "readonly": False,
                "hidden": False,
                "order": 1,
                "css_class": "username-input",
                "width": "50%",
                "icon": "user",
            },
            "options": {
                "searchable": True,
                "sortable": True,
                "unique": True,
                "index": True,
                "default_sort": False,
                "filterable": True,
                "group": "Account Information",
                "dependencies": ["email", "password"],
            },
        }


class FieldSchema(Schema):
    id = fields.Int()
    collection = fields.Str()
    field = fields.Str()
    type = fields.Str()
    schema = fields.Dict()
    interface = fields.Dict()
    options = fields.Dict()

    class Meta:
        model = FieldModel
