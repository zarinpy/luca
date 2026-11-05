import pytest
from typer.testing import CliRunner

from luca.cli import app

runner = CliRunner()


class FakeDatabase:
    def __init__(self, url: str) -> None:
        self.url = url
        self.disposed = False

    def dispose(self) -> None:
        self.disposed = True


def test_cli_insert_basedata(monkeypatch: pytest.MonkeyPatch) -> None:
    opened: list[FakeDatabase] = []

    def open_database(url: str) -> FakeDatabase:
        database = FakeDatabase(url)
        opened.append(database)
        return database

    calls = []
    monkeypatch.setattr("luca.cli.Database", open_database)
    monkeypatch.setattr(
        "luca.basedata.insert",
        lambda database: calls.append(database),
    )

    result = runner.invoke(app, ["db", "basedata", "insert"])

    assert result.exit_code == 0
    assert calls == opened
    assert opened[0].disposed is True


def test_cli_insert_basedata_disposes_on_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    opened: list[FakeDatabase] = []

    def open_database(url: str) -> FakeDatabase:
        database = FakeDatabase(url)
        opened.append(database)
        return database

    def fail(database: object) -> None:
        del database
        message = "insert failed"
        raise RuntimeError(message)

    monkeypatch.setattr("luca.cli.Database", open_database)
    monkeypatch.setattr("luca.basedata.insert", fail)

    result = runner.invoke(app, ["db", "basedata", "insert"])

    assert result.exit_code != 0
    assert opened[0].disposed is True


def test_cli_insert_mockup(monkeypatch: pytest.MonkeyPatch) -> None:
    opened: list[FakeDatabase] = []

    def open_database(url: str) -> FakeDatabase:
        database = FakeDatabase(url)
        opened.append(database)
        return database

    calls = []
    monkeypatch.setattr("luca.cli.Database", open_database)
    monkeypatch.setattr(
        "luca.mockup.insert",
        lambda database: calls.append(database),
    )

    result = runner.invoke(app, ["db", "mockup", "insert"])

    assert result.exit_code == 0
    assert calls == opened
    assert opened[0].disposed is True


def test_revision_autodetects_model_changes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen = {}

    def fake_revision(*args: object, **kwargs: object) -> None:
        del args
        seen["message"] = kwargs["message"]
        seen["autogenerate"] = kwargs["autogenerate"]

    monkeypatch.setattr("luca.cli.command.revision", fake_revision)

    result = runner.invoke(app, ["db", "revision", "-m", "add member"])

    assert result.exit_code == 0
    assert seen == {"message": "add member", "autogenerate": True}


def test_revision_empty_skips_autogenerate(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen = {}

    def fake_revision(*args: object, **kwargs: object) -> None:
        del args
        seen["autogenerate"] = kwargs["autogenerate"]

    monkeypatch.setattr("luca.cli.command.revision", fake_revision)

    result = runner.invoke(
        app,
        ["db", "revision", "-m", "data only", "--empty"],
    )

    assert result.exit_code == 0
    assert seen["autogenerate"] is False
