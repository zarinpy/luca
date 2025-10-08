from fastapi import APIRouter, Request, status

taxonomy_router = APIRouter(prefix="/taxonomies", tags=["Taxonomies"])


@taxonomy_router.get("/", status_code=status.HTTP_200_OK)
async def get_all_taxonomies(request: Request) -> None :
    pass


@taxonomy_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_taxonomy(request: Request) -> None :
    pass


@taxonomy_router.get("/{taxonomy_id}", status_code=status.HTTP_200_OK)
async def get_taxonomy(taxonomy_id: int, request: Request) -> None :
    pass


@taxonomy_router.put("/{taxonomy_id}", status_code=status.HTTP_200_OK)
async def update_taxonomy(taxonomy_id: int, request: Request) -> None :
    pass


@taxonomy_router.delete("/{taxonomy_id}",
                        status_code=status.HTTP_204_NO_CONTENT)
async def delete_taxonomy(taxonomy_id: int, request: Request) -> None :
    pass
