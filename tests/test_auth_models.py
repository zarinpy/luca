import pytest

from luca.auth.models import Member, MemberLocale
from luca.common.i18n import full_name
from luca.locale.models import Locale


def _locale(code: str, name: str) -> Locale:
    return Locale(code=code, name=name)


def _catalog() -> list[Locale]:
    return [
        _locale("en-US", "English (United States)"),
        _locale("fa-IR", "Persian (Iran)"),
        _locale("de-DE", "German (Germany)"),
    ]


class _Result:
    def __init__(self, rows: list[object]) -> None:
        self.rows = rows

    def first(self) -> object | None:
        if not self.rows:
            return None
        return self.rows[0]

    def all(self) -> list[object]:
        return list(self.rows)


class _Session:
    def __init__(
        self,
        member: Member | None = None,
        locales: list[Locale] | None = None,
    ) -> None:
        self.member = member
        self.locales = list(locales or _catalog())
        self.added: list[object] = []

    def scalars(self, statement: object) -> _Result:
        entity = statement.column_descriptions[0]["entity"]
        if entity is Locale:
            return _Result(self.locales)
        return _Result([] if self.member is None else [self.member])

    def add(self, row: object) -> None:
        self.added.append(row)

    def flush(self) -> None:
        return None


def test_translated_fields_live_on_memberlocale() -> None:
    member_columns = set(Member.__table__.c.keys())
    locale_columns = set(MemberLocale.__table__.c.keys())
    assert "name" not in member_columns
    assert "family" not in member_columns
    assert {"name", "family", "member_id", "locale_id"} <= locale_columns
    targets = {
        key.column.table.name for key in MemberLocale.__table__.foreign_keys
    }
    assert targets == {"member", "locale"}


def test_ensure_stores_family_on_a_locale_row() -> None:
    session = _Session()

    created = Member.ensure(
        session,
        "sara@example.com",
        "Sara",
        family="Smith",
        translations={
            "fa-IR": {"name": "سارا", "family": "اسمیت"},
        },
    )

    assert session.added == [created]
    assert created.name == "Sara"
    assert created.roles == ["user"]
    assert full_name(created, "en-US") == "Sara Smith"
    assert created.display_name("fa-IR") == "سارا اسمیت"
    assert created.text("family", "de-DE") == "Smith"
    stored = {
        row.locale.code: (row.name, row.family)
        for row in created.translations
    }
    assert stored == {
        "en-US": ("Sara", "Smith"),
        "fa-IR": ("سارا", "اسمیت"),
    }


def test_ensure_keeps_existing_translations() -> None:
    english = _locale("en-US", "English (United States)")
    persian = _locale("fa-IR", "Persian (Iran)")
    existing = Member(email="sara@example.com", roles=["user"])
    existing.translations.append(
        MemberLocale(locale=english, name="Sara", family="Smith"),
    )
    existing.translations.append(
        MemberLocale(locale=persian, name="سارا", family="اسمیت"),
    )
    session = _Session(existing)

    member = Member.ensure(
        session,
        "sara@example.com",
        "Ignored",
        family="Ignored",
        translations={"fa-IR": {"name": "دیگر"}},
    )

    assert member is existing
    assert session.added == []
    assert member.name == "Sara"
    assert member.text("family", "fa-IR") == "اسمیت"


def test_ensure_rejects_unknown_text_field() -> None:
    with pytest.raises(ValueError, match="unknown member text field"):
        Member.ensure(
            _Session(),
            "sara@example.com",
            "Sara",
            translations={"fa-IR": {"title": "Teacher"}},
        )


def test_ensure_rejects_unknown_locale() -> None:
    with pytest.raises(ValueError, match="unknown locale"):
        Member.ensure(
            _Session(locales=_catalog()),
            "sara@example.com",
            "Sara",
            translations={"xx-XX": {"name": "Sara"}},
        )


def test_builtin_names_keep_their_roles() -> None:
    god = Member.ensure(_Session(), "god@example.com", "God")
    admin = Member.ensure(_Session(), "admin@example.com", "Admin")

    assert god.roles == ["god"]
    assert god.display_name() == "God"
    assert admin.roles == ["admin"]
