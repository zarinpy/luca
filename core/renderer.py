import copy
from typing import Any, Dict, List, Optional

import ujson
from fastapi import status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.background import BackgroundTask

__all__ = ["CustomResponse", "get_response_schema"]


class CustomResponse(JSONResponse):
    content: Any = None

    def __init__(
            self,
            content: Any = None,
            message: str = "",
            metadata: Dict[str, Any] = {},
            details: Any = None,
            status_code: int = status.HTTP_200_OK,
            headers: Dict = None,
            media_type: str = None,
            background: BackgroundTask = None,
    ) -> None:
        self.content = content
        self.metadata = metadata
        self.message = message
        self.details = details
        super(CustomResponse, self).__init__(
            content, status_code, headers, media_type, background
        )

    def clean(self):
        if not self.content:
            self.content = []
        if not self.details:
            self.details = {}

        result = {
            "info": {
                "message": self.message,
                "details": self.details,
                "metadata": self.metadata,
            },
            "data": self.content,
        }
        return result

    def render(self, content: Any) -> bytes:
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
    details: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}


# Define the generic Response model
class APIResponse(BaseModel):
    info: Info
    data: Dict[str, Any] = {}


# Utility function to create APIResponse with custom message
def create_response(
        status_code: int,
        message: Optional[str] = None,
        data: Dict[str, Any] = None,
        details: Dict[str, Any] = None,
        metadata: Dict[str, Any] = None
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
    response = APIResponse(
        info=Info(
            message=final_message,
            details=details or {},
            metadata=metadata or {}
        ),
        data=data or {}
    )

    return response


# Define response schema for OpenAPI documentation
def get_response_schema(status_code: int, message: str) -> Dict:
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
                            "metadata": {}
                        },
                        "data": {}
                    }
                }
            }
        }
    }
