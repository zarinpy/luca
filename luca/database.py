import re
from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, make_url
from sqlalchemy.orm import Session, sessionmaker

_DATABASE_NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


class Database:
    """Sync SQLAlchemy access used by basedata and mockup."""

    def __init__(self, url: str) -> None:
        self.engine = create_engine(url, pool_pre_ping=True)
        self._session_factory = sessionmaker(
            bind=self.engine,
            expire_on_commit=False,
        )

    @contextmanager
    def session(self) -> Iterator[Session]:
        db_session = self._session_factory()
        try:
            yield db_session
        finally:
            db_session.close()

    def dispose(self) -> None:
        self.engine.dispose()


def database_name(url: str) -> str:
    name = make_url(url).database
    if name is None or _DATABASE_NAME.fullmatch(name) is None:
        message = f"unsupported database name: {name}"
        raise ValueError(message)
    return name


def _admin_engine(url: str) -> Engine:
    admin_url = make_url(url).set(database="postgres")
    return create_engine(
        admin_url,
        isolation_level="AUTOCOMMIT",
        pool_pre_ping=True,
    )


def create_database(url: str) -> str:
    """
    Create the database when it is missing.

    Returns ``created`` or ``exists``.
    """
    name = database_name(url)
    engine = _admin_engine(url)
    try:
        with engine.connect() as connection:
            exists = connection.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :name"),
                {"name": name},
            ).scalar()
            if exists:
                return "exists"
            # `name` is restricted to a plain identifier above.
            connection.execute(text(f'CREATE DATABASE "{name}"'))
    finally:
        engine.dispose()
    return "created"


def drop_database(url: str) -> None:
    """Drop the configured database if it exists."""
    name = database_name(url)
    engine = _admin_engine(url)
    try:
        with engine.connect() as connection:
            connection.execute(
                text(
                    "SELECT pg_terminate_backend(pid) "
                    "FROM pg_stat_activity "
                    "WHERE datname = :name "
                    "AND pid <> pg_backend_pid()",
                ),
                {"name": name},
            )
            # `name` is restricted to a plain identifier above.
            connection.execute(
                text(f'DROP DATABASE IF EXISTS "{name}"'),
            )
    finally:
        engine.dispose()
