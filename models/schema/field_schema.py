import uuid
from typing import Optional, List, Literal, Union
from marshmallow import Schema, fields
from pydantic import BaseModel, Field
from models.orm_models.core import Field as FieldModel


__all__ = ["CreateField", "FieldSchema"]


class SchemaDefinition(BaseModel):
    type: Literal[
        "string", "integer", "number", "boolean",
        "array", "object", "date", "datetime"
    ] = Field(..., description="Data type of the field")
    required: Optional[bool] = Field(
        False,
        description="Indicates if the field is required"
    )
    default: Optional[Union[str, int, float, bool, list, dict]] = Field(
        None,
        description="Default value for the field"
    )
    enum: Optional[List[Union[str, int]]] = Field(
        None,
        description="List of allowed values"
    )
    min_length: Optional[int] = Field(
        None,
        description="Minimum length for string fields"
    )
    max_length: Optional[int] = Field(
        None,
        description="Maximum length for string fields"
    )
    minimum: Optional[float] = Field(
        None,
        description="Minimum value for numeric fields"
    )
    maximum: Optional[float] = Field(
        None,
        description="Maximum value for numeric fields"
    )
    pattern: Optional[str] = Field(
        None,
        description="Regex pattern for string fields"
    )
    items: Optional["SchemaDefinition"] = Field(
        None,
        description="Schema definition for items in array fields"
    )

    class Config:
        extra = "forbid"


class InterfaceSettings(BaseModel):
    widget: Optional[str] = Field(
        None,
        description="Type of UI widget (e.g., 'text', 'select', 'checkbox')"
    )
    label: Optional[str] = Field(
        None,
        description="Label displayed for the field"
    )
    placeholder: Optional[str] = Field(
        None,
        description="Placeholder text for the field"
    )
    help_text: Optional[str] = Field(
        None,
        description="Help text or tooltip for the field"
    )
    readonly: Optional[bool] = Field(
        False,
        description="Indicates if the field is read-only"
    )
    hidden: Optional[bool] = Field(
        False,
        description="Indicates if the field is hidden in the UI"
    )
    order: Optional[int] = Field(
        None,
        description="Order of the field in the UI"
    )
    css_class: Optional[str] = Field(
        None,
        description="CSS class for styling the field"
    )
    width: Optional[str] = Field(
        None,
        description="Width of the field in the UI (e.g., '50%')"
    )
    icon: Optional[str] = Field(
        None,
        description="Icon associated with the field"
    )

    class Config:
        extra = "forbid"


class AdditionalOptions(BaseModel):
    searchable: Optional[bool] = Field(
        False, description="Indicates if the field is searchable"
    )
    sortable: Optional[bool] = Field(
        False, description="Indicates if the field is sortable"
    )
    unique: Optional[bool] = Field(
        False, description="Indicates if the field value must be unique"
    )
    index: Optional[bool] = Field(
        False, description="Indicates if the field should be indexed in the database"
    )
    default_sort: Optional[bool] = Field(
        False, description="Indicates if the field is used for default sorting"
    )
    filterable: Optional[bool] = Field(
        False, description="Indicates if the field can be used for filtering"
    )
    group: Optional[str] = Field(
        None, description="Group name for organizing fields in the UI"
    )
    dependencies: Optional[List[str]] = Field(
        None, description="List of field names this field depends on"
    )

    class Config:
        extra = "forbid"


class CreateField(BaseModel):
    collection: uuid.UUID = Field(..., description="CreateCollection this field belongs to")
    field: str = Field(..., description="Name of the field")
    type: str = Field(..., description="Data type of the field")
    schema: Optional[SchemaDefinition] = Field(
        None, description="Schema definition for the field"
    )
    interface: Optional[InterfaceSettings] = Field(
        None, description="UI settings for the field"
    )
    options: Optional[AdditionalOptions] = Field(
        None, description="Additional options for the field"
    )

    class Config:
        extra = "forbid"
        json_schema_extra = {
          "collection_id": uuid.uuid4(),
          "field": "username",
          "type": "string",
          "schema": {
            "type": "string",
            "required": True,
            "default": "guest_user",
            "enum": ["guest_user", "admin_user", "regular_user"],
            "min_length": 5,
            "max_length": 20,
            "pattern": "^[a-zA-Z0-9_]+$"
          },
          "interface": {
            "widget": "text",
            "label": "Username",
            "placeholder": "Enter your username",
            "help_text": "Username must be 5-20 characters long and can include letters, numbers, and underscores.",
            "readonly": False,
            "hidden": False,
            "order": 1,
            "css_class": "username-input",
            "width": "50%",
            "icon": "user"
          },
          "options": {
            "searchable": True,
            "sortable": True,
            "unique": True,
            "index": True,
            "default_sort": False,
            "filterable": True,
            "group": "Account Information",
            "dependencies": ["email", "password"]
          }
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
