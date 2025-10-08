from fastapi import APIRouter, Request, status

role_router = APIRouter(prefix="/roles", tags=["Roles"])


@role_router.get("/", status_code=status.HTTP_200_OK)
async def list_roles(request: Request) -> None :
    """List all roles"""


@role_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_role(request: Request) -> None :
    """Create a new role"""


@role_router.get("/{role_id}", status_code=status.HTTP_200_OK)
async def retrieve_role(request: Request, role_id: str) -> None :
    """Retrieve a role by ID"""


@role_router.patch("/{role_id}", status_code=status.HTTP_200_OK)
async def update_role(request: Request, role_id: str) -> None :
    """Update a role by ID"""


@role_router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(request: Request, role_id: str) -> None :
    """Delete a role by ID"""
