import pytest

from luca.config import get_settings


def test_settings_read_db_uri_from_the_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "DB_URI",
        "postgresql+psycopg://localhost/example",
    )
    get_settings.cache_clear()
    try:
        assert get_settings().db_uri == (
            "postgresql+psycopg://localhost/example"
        )
    finally:
        get_settings.cache_clear()
