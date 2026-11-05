from types import SimpleNamespace
from typing import Self

import pytest

from luca import basedata
from luca.auth import basedata as auth_basedata
from luca.site import basedata as site_basedata
from luca.site.models import DEFAULTS, SINGLETON_ID, SiteSettings


def test_insert_delegates_to_module_basedata(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    calls = []
    monkeypatch.setattr(
        auth_basedata,
        "insert",
        lambda db: calls.append(("auth", db)),
    )
    monkeypatch.setattr(
        site_basedata,
        "insert",
        lambda db: calls.append(("site", db)),
    )

    db = SimpleNamespace(engine=SimpleNamespace(url="postgresql://test"))
    basedata.insert(db)

    assert calls == [("auth", db), ("site", db)]
    output = capsys.readouterr().out
    assert "generate base data, db url: postgresql://test" in output


class FakeSession:
    def __init__(self) -> None:
        self.added: list[object] = []
        self.committed = False
        self.existing: SiteSettings | None = None

    def add(self, row: object) -> None:
        self.added.append(row)

    def commit(self) -> None:
        self.committed = True

    def get(self, model: type[object], key: int) -> SiteSettings | None:
        if model is SiteSettings and key == SINGLETON_ID:
            return self.existing
        return None

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: object,
        exc: object,
        traceback: object,
    ) -> bool:
        return False


def test_site_basedata_inserts_singleton_defaults() -> None:
    session = FakeSession()
    db = SimpleNamespace(session=lambda: session)

    site_basedata.insert(db)

    assert session.committed is True
    assert len(session.added) == 1
    row = session.added[0]
    assert isinstance(row, SiteSettings)
    assert row.id == SINGLETON_ID
    assert row.name == DEFAULTS["name"]
    assert row.email == DEFAULTS["email"]


def test_site_basedata_skips_when_singleton_exists() -> None:
    session = FakeSession()
    session.existing = SiteSettings(id=SINGLETON_ID, **DEFAULTS)
    db = SimpleNamespace(session=lambda: session)

    site_basedata.insert(db)

    assert session.added == []
    assert session.committed is False


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
