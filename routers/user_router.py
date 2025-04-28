from fastapi import APIRouter, Request, status

user_router = APIRouter(prefix="/users", tags=["Users"])


@user_router.get("/", status_code=status.HTTP_200_OK)
async def list_users(request: Request):
    """Get a list of all users"""


@user_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(request: Request):
    """Create a new user"""


@user_router.get("/{user_id}", status_code=status.HTTP_200_OK)
async def retrieve_user(request: Request, user_id: str):
    """Retrieve a user by ID"""


@user_router.patch("/{user_id}", status_code=status.HTTP_200_OK)
async def update_user(request: Request, user_id: str):
    """Update a user by ID"""


@user_router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(request: Request, user_id: str):
    """Delete a user by ID"""


@user_router.patch("/{user_id}/activate", status_code=status.HTTP_200_OK)
async def activate_user(user_id: int, request: Request):
    pass
