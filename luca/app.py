from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from luca.config import ROOT, Settings, get_settings
from luca.database import Database
from luca.manifest import __version__
from luca.templating import MakoTemplates

PACKAGE_DIR = Path(__file__).resolve().parent


@asynccontextmanager
async def _lifespan(app: FastAPI) -> AsyncIterator[None]:
    yield
    database = getattr(app.state, "db", None)
    if isinstance(database, Database):
        database.dispose()


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    app = FastAPI(
        title=settings.app_name,
        version=__version__,
        debug=settings.debug,
        lifespan=_lifespan,
    )
    templates = MakoTemplates(
        PACKAGE_DIR / "templates",
        ROOT / ".var" / "mako",
    )
    app.state.settings = settings
    app.state.db = Database(settings.db_uri)
    app.state.templates = templates

    @app.get("/", response_class=HTMLResponse)
    def index() -> HTMLResponse:
        body = templates.render("index.mako", settings=settings)
        return HTMLResponse(body)

    return app
