from fastapi import APIRouter, Request, status

auth_route = APIRouter(prefix="/auth", tags=["Auth"])


@auth_route.post("/login", status_code=status.HTTP_200_OK)
async def login(request: Request):
    pass


@auth_route.post("/logout", status_code=status.HTTP_200_OK)
async def logout(request: Request):
    pass


@auth_route.post("/refresh-token", status_code=status.HTTP_200_OK)
async def refresh_token(request: Request):
    pass


@auth_route.post("/password-reset", status_code=status.HTTP_200_OK)
async def password_reset(request: Request):
    pass
