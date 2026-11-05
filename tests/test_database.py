import pytest

from luca.database import database_name


def test_database_name() -> None:
    url = "postgresql+psycopg://postgres@localhost:5432/luca"
    assert database_name(url) == "luca"


def test_database_name_rejects_unsafe_names() -> None:
    url = 'postgresql+psycopg://localhost/bad"name'
    with pytest.raises(ValueError, match="unsupported database name"):
        database_name(url)
