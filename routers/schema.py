from fastapi import APIRouter, Request, status

schemas_route = APIRouter(prefix="/schemas", tags=["Schemas"])


@schemas_route.get("/", status_code=status.HTTP_200_OK)
async def get_schemas(request: Request):
    pass
