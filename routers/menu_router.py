from fastapi import APIRouter, Request, status

menu_router = APIRouter(prefix="/menus", tags=["Menus"])


@menu_router.get("/", status_code=status.HTTP_200_OK)
async def get_all_menus(request: Request) -> None :
    pass


@menu_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_menu(request: Request) -> None :
    pass


@menu_router.get("/{menu_id}", status_code=status.HTTP_200_OK)
async def get_menu(menu_id: int, request: Request) -> None :
    pass


@menu_router.put("/{menu_id}", status_code=status.HTTP_200_OK)
async def update_menu(menu_id: int, request: Request) -> None :
    pass


@menu_router.delete("/{menu_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_menu(menu_id: int, request: Request) -> None :
    pass


@menu_router.post("/{menu_id}/items/", status_code=status.HTTP_201_CREATED)
async def create_menu_item(menu_id: int, request: Request) -> None :
    pass


@menu_router.put("/items/{item_id}", status_code=status.HTTP_200_OK)
async def update_menu_item(item_id: int, request: Request) -> None :
    pass


@menu_router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_menu_item(item_id: int, request: Request) -> None :
    pass
