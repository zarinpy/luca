from pathlib import Path
from typing import Annotated

import typer
import uvicorn
from alembic import command
from alembic.config import Config

from luca import basedata, mockup
from luca.config import ROOT, get_settings
from luca.database import (
    Database,
    create_database,
    database_name,
    drop_database,
)
from luca.i18n import (
    CatalogError,
    compile_catalogs,
    translate,
)

app = typer.Typer(no_args_is_help=True)
db_app = typer.Typer(no_args_is_help=True)
basedata_app = typer.Typer(no_args_is_help=True)
mockup_app = typer.Typer(no_args_is_help=True)
i18n_app = typer.Typer(no_args_is_help=True)
app.add_typer(db_app, name="db")
db_app.add_typer(basedata_app, name="basedata")
db_app.add_typer(mockup_app, name="mockup")
app.add_typer(i18n_app, name="i18n")


def alembic_config() -> Config:
    cfg = Config(str(ROOT / "alembic.ini"))
    cfg.set_main_option("script_location", str(ROOT / "migrations"))
    # ConfigParser treats "%" as interpolation syntax.
    url = get_settings().db_uri.replace("%", "%%")
    cfg.set_main_option("sqlalchemy.url", url)
    return cfg


def _open_database() -> Database:
    return Database(get_settings().db_uri)


def _insert_basedata() -> None:
    database = _open_database()
    try:
        basedata.insert(database)
    finally:
        database.dispose()


def _insert_mockup() -> None:
    database = _open_database()
    try:
        mockup.insert(database)
    finally:
        database.dispose()


@basedata_app.command("insert")
def basedata_insert() -> None:
    """Insert required base rows."""
    _insert_basedata()


@mockup_app.command("insert")
def mockup_insert() -> None:
    """Insert sample rows."""
    _insert_mockup()


@db_app.command("create")
def db_create() -> None:
    """Create the configured database when it does not exist."""
    url = get_settings().db_uri
    name = database_name(url)
    state = create_database(url)
    if state == "exists":
        typer.echo(f"database {name} already exists")
        return
    typer.echo(f"created database {name}")


@db_app.command("drop")
def db_drop() -> None:
    """Drop the configured database."""
    url = get_settings().db_uri
    name = database_name(url)
    drop_database(url)
    typer.echo(f"dropped database {name}")


@db_app.command()
def upgrade(
    revision: Annotated[str, typer.Argument()] = "head",
) -> None:
    """Apply migrations."""
    command.upgrade(alembic_config(), revision)


@db_app.command()
def downgrade(
    revision: Annotated[str, typer.Argument()] = "-1",
) -> None:
    """Revert migrations."""
    command.downgrade(alembic_config(), revision)


@db_app.command()
def current() -> None:
    """Show the current migration revision."""
    command.current(alembic_config())


@db_app.command()
def revision(
    message: Annotated[
        str,
        typer.Option("--message", "-m", help="Migration summary."),
    ],
    *,
    empty: Annotated[
        bool,
        typer.Option(
            "--empty",
            help="Create a revision without comparing models.",
        ),
    ] = False,
) -> None:
    """Write a migration by detecting model changes."""
    command.revision(
        alembic_config(),
        message=message,
        autogenerate=not empty,
    )


@db_app.command()
def rebuild() -> None:
    """
    Drop and recreate the database, then migrate and seed it.

    This deletes the configured database.
    """
    url = get_settings().db_uri
    drop_database(url)
    create_database(url)
    command.upgrade(alembic_config(), "head")
    _insert_basedata()
    _insert_mockup()


def _display_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(ROOT).as_posix()
    except ValueError:
        return str(resolved)


@i18n_app.command("translate")
def i18n_translate() -> None:
    """Extract messages and update catalogs for every locale."""
    try:
        result = translate()
    except CatalogError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc
    typer.echo(f"extracted {_display_path(result.template)}")
    for code in result.initialized:
        typer.echo(f"initialized {code}")
    for code in result.updated:
        typer.echo(f"updated {code}")


@i18n_app.command("compile")
def i18n_compile() -> None:
    """Compile message catalogs to MO files."""
    try:
        compiled = compile_catalogs()
    except CatalogError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc
    for code in compiled:
        typer.echo(f"compiled {code}")


@app.command()
def serve(
    host: Annotated[str | None, typer.Option()] = None,
    port: Annotated[int | None, typer.Option()] = None,
    *,
    reload: Annotated[bool, typer.Option()] = True,
) -> None:
    """Run the development server."""
    settings = get_settings()
    uvicorn.run(
        "luca.app:create_app",
        factory=True,
        host=host or settings.host,
        port=port or settings.port,
        reload=reload,
    )


def main() -> None:
    app()
