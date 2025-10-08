from fastapi import APIRouter, Request, status

permission_router = APIRouter(prefix="/permissions", tags=["Permissions"])


@permission_router.get("/", status_code=status.HTTP_200_OK)
async def list_permissions(request: Request) -> None :
    """List all permissions"""


@permission_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_permission(request: Request) -> None :
    """Create a new permission"""


@permission_router.get("/{permission_id}", status_code=status.HTTP_200_OK)
async def retrieve_permission(request: Request, permission_id: str) -> None :
    """Retrieve a permission by ID"""


@permission_router.patch("/{permission_id}", status_code=status.HTTP_200_OK)
async def update_permission(request: Request, permission_id: str) -> None :
    """Update a permission by ID"""


@permission_router.delete("/{permission_id}",
                          status_code=status.HTTP_204_NO_CONTENT)
async def delete_permission(request: Request, permission_id: str) -> None :
    """Delete a permission by ID"""
