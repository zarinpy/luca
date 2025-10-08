from fastapi.routing import APIRouter

from .collection_router import collections_router
from .menu_router import menu_router
from .permission_router import permission_router
from .role_router import role_router
from .taxonomy_router import taxonomy_router
from .user_router import user_router

routes = APIRouter(prefix="/api")
routes.include_router(user_router)
routes.include_router(collections_router)
routes.include_router(permission_router)
routes.include_router(role_router)
routes.include_router(taxonomy_router)
routes.include_router(menu_router)
