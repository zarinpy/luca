from fastapi import APIRouter, Request, status

translation_route = APIRouter(prefix="/translations", tags=["Translations"])


@translation_route.get("/", status_code=status.HTTP_200_OK)
async def get_all_translations(request: Request):
    pass


@translation_route.post("/", status_code=status.HTTP_201_CREATED)
async def create_translation(request: Request):
    pass


@translation_route.get("/{translation_id}", status_code=status.HTTP_200_OK)
async def get_translation(translation_id: int, request: Request):
    pass


@translation_route.put("/{translation_id}", status_code=status.HTTP_200_OK)
async def update_translation(translation_id: int, request: Request):
    pass


@translation_route.delete("/{translation_id}",
                          status_code=status.HTTP_204_NO_CONTENT)
async def delete_translation(translation_id: int, request: Request):
    pass
