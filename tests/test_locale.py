from types import SimpleNamespace
from typing import Self

from luca.i18n import LOCALES
from luca.locale import basedata
from luca.locale.models import Locale


class _Rows:
    def __init__(self, rows: list[Locale]) -> None:
        self.rows = rows

    def all(self) -> list[Locale]:
        return list(self.rows)


class _Session:
    def __init__(self, codes: list[str] | None = None) -> None:
        self.present = [
            Locale(code=code, name=code) for code in (codes or [])
        ]
        self.added: list[Locale] = []
        self.committed = False

    def scalars(self, statement: object) -> _Rows:
        del statement
        return _Rows(self.present)

    def add(self, row: Locale) -> None:
        self.added.append(row)

    def commit(self) -> None:
        self.committed = True

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: object,
        exc: object,
        traceback: object,
    ) -> bool:
        return False


def test_locale_basedata_inserts_every_supported_code() -> None:
    session = _Session()
    basedata.insert(SimpleNamespace(session=lambda: session))

    assert session.committed is True
    assert [row.code for row in session.added] == [code for _, code in LOCALES]
    assert session.added[0].name == "English (United States)"


def test_locale_basedata_skips_codes_that_exist() -> None:
    session = _Session(["en-US", "fa-IR"])
    basedata.insert(SimpleNamespace(session=lambda: session))

    added = {row.code for row in session.added}
    assert "en-US" not in added
    assert "fa-IR" not in added
    assert len(session.added) == len(LOCALES) - 2
