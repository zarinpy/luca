from types import SimpleNamespace

import pytest

from luca import mockup
from luca.auth import mockup as auth_mockup


def test_insert_delegates_to_module_mockup(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    calls = []
    monkeypatch.setattr(
        auth_mockup,
        "insert",
        lambda db: calls.append(("auth", db)),
    )
    db = SimpleNamespace(engine=SimpleNamespace(url="postgresql://test"))

    mockup.insert(db)

    assert calls == [("auth", db)]
    output = capsys.readouterr().out
    assert "generating mockup data, db url: postgresql://test" in output
    assert "mockup data generation done" in output


def test_auth_mockup_inserts_sample_users(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    seen = []

    def record(db: object, members: list[tuple[str, str]]) -> None:
        seen.append((db, members))

    monkeypatch.setattr(auth_mockup, "ensure_members", record)
    db = object()

    auth_mockup.insert(db)

    assert seen == [
        (
            db,
            [
                ("Bob", "bob@example.com"),
                ("Alice", "alice@example.com"),
            ],
        ),
    ]
    output = capsys.readouterr().out
    assert "generating authentication module's mockup data" in output
