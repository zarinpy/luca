from fastapi import APIRouter, Request, status

content_router = APIRouter(prefix="/contents", tags=["Contents"])


@content_router.get("/", status_code=status.HTTP_200_OK)
async def get_all_content(request: Request):
    pass


@content_router.get("/{content_id}", status_code=status.HTTP_200_OK)
async def get_content(content_id: int, request: Request):
    pass


@content_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_content(request: Request):
    pass


@content_router.put("/{content_id}", status_code=status.HTTP_200_OK)
async def update_content(content_id: int, request: Request):
    pass


@content_router.delete("/{content_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_content(content_id: int, request: Request):
    pass


@content_router.patch("/{content_id}/publish", status_code=status.HTTP_200_OK)
async def publish_content(content_id: int, request: Request):
    pass


@content_router.get("/drafts/", status_code=status.HTTP_200_OK)
async def get_drafts(request: Request):
    pass


@content_router.post("/{content_id}/revisions/",
                     status_code=status.HTTP_201_CREATED)
async def save_revision(content_id: int, request: Request):
    pass
