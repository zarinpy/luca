from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import ujson
from fastapi import status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

if TYPE_CHECKING:
    from starlette.background import BackgroundTask

__all__ = ["CustomResponse", "get_response_schema"]

@dataclass
class ResponseInfo:
    details: dict | None = None
    metadata: dict[str, Any] = None
    message: str = ""

class CustomResponse(JSONResponse):
    content: Any = None

    def __init__(   #noqa: PLR0913
            self,
            content: dict | list | None,
            info: ResponseInfo,
            headers: dict | None = None,
            media_type: str | None = None,
            background: BackgroundTask | None = None,
            status_code: int = status.HTTP_200_OK,
    ) -> None:
        self.content = content
        self.details = info.details
        self.metadata = info.metadata
        self.message = info.message
        super().__init__(
            content, status_code, headers, media_type, background,
        )

    def clean(self) -> dict[str, Any]:
        if not self.content:
            self.content = []
        if not self.details:
            self.details = {}

        return {
            "info": {
                "message": self.message,
                "details": self.details,
                "metadata": self.metadata,
            },
            "data": self.content,
        }

    def render(self, content: list | dict) -> bytes:
        content = self.clean()
        return ujson.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            default=str,
            separators=(",", ":"),
        ).encode("utf-8")


# Define the Info model
class Info(BaseModel):
    message: str
    details: dict[str, Any] = {}
    metadata: dict[str, Any] = {}


# Define the generic Response model
class APIResponse(BaseModel):
    info: Info
    data: dict[str, Any] = {}


# Utility function to create APIResponse with custom message
def create_response(
        status_code: int,
        message: str | None,
        data: dict[str, Any],
        details: dict[str, Any],
        metadata: dict[str, Any],
) -> APIResponse:
    # Default messages based on status code
    status_messages = {
        200: "Success",
        201: "Resource Name created successfully",
        400: "Bad request",
        422: "Invalid Content send",
        404: "Item not found",
    }

    # Use custom message if provided, else fall back to default
    final_message = message or status_messages.get(
        status_code,
        "Unknown error",
    )

    # Create the response
    return APIResponse(
        info=Info(
            message=final_message,
            details=details or {},
            metadata=metadata or {},
        ),
        data=data or {},
    )


# Define response schema for OpenAPI documentation
def get_response_schema(status_code: int, message: str) -> dict:
    return {
        status_code: {
            "model": APIResponse,
            "description": message,
            "content": {
                "application/json": {
                    "example": {
                        "info": {
                            "message": message,
                            "details": {},
                            "metadata": {},
                        },
                        "data": {},
                    },
                },
            },
        },
    }
