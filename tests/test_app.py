from http import HTTPStatus

from fastapi.testclient import TestClient

from luca.app import create_app
from luca.common.models import Base
from luca.config import Settings


def test_index_renders_mako() -> None:
    app = create_app(
        Settings(db_uri="postgresql+psycopg://localhost/luca"),
    )
    with TestClient(app) as client:
        response = client.get("/")

    assert response.status_code == HTTPStatus.OK
    assert "<h1>luca</h1>" in response.text
    assert 'lang="en-US"' in response.text
    assert "FastAPI and Mako" in response.text


def test_metadata_registers_models() -> None:
    import luca.models

    assert luca.models.__all__ == [
        "Locale",
        "Member",
        "MemberLocale",
    ]
    assert "locale" in Base.metadata.tables
    assert "member" in Base.metadata.tables
    assert "memberlocale" in Base.metadata.tables
    assert "sitesettings" not in Base.metadata.tables
