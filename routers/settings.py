from fastapi import APIRouter, Request, status

settings_route = APIRouter(prefix="/settings", tags=["Settings"])


@settings_route.get("/", status_code=status.HTTP_200_OK)
async def get_settings(request: Request) -> None :
    pass


@settings_route.put("/", status_code=status.HTTP_200_OK)
async def update_settings(request: Request) -> None :
    pass
