from types import SimpleNamespace

import pytest

from luca import basedata
from luca.auth import basedata as auth_basedata
from luca.locale import basedata as locale_basedata


def test_insert_delegates_to_module_basedata(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    calls = []
    monkeypatch.setattr(
        locale_basedata,
        "insert",
        lambda db: calls.append(("locale", db)),
    )
    monkeypatch.setattr(
        auth_basedata,
        "insert",
        lambda db: calls.append(("auth", db)),
    )

    db = SimpleNamespace(engine=SimpleNamespace(url="postgresql://test"))
    basedata.insert(db)

    assert calls == [("locale", db), ("auth", db)]
    output = capsys.readouterr().out
    assert "generate base data, db url: postgresql://test" in output


def test_auth_basedata_inserts_builtin_users(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    seen = []

    def record(db: object, members: list[tuple[str, str]]) -> None:
        seen.append((db, members))

    monkeypatch.setattr(auth_basedata, "ensure_members", record)
    db = object()

    auth_basedata.insert(db)

    assert seen == [
        (
            db,
            [
                ("God", "god@example.com"),
                ("Admin", "admin@example.com"),
            ],
        ),
    ]
    output = capsys.readouterr().out
    assert "generating authentication module's base data" in output
