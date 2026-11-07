from __future__ import annotations

from sqlalchemy import ForeignKey, String, UniqueConstraint, select
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from luca.common.datetime import utcnow
from luca.common.i18n import DEFAULT_CODE, TEXT_FIELDS, full_name, pick
from luca.common.models import Base, TimestampMixin
from luca.locale.models import Locale

from .basedata import ADMINS, GODS


def roles_for(name: str) -> list[str]:
    if name in GODS:
        return ["god"]
    if name in ADMINS:
        return ["admin"]
    return ["user"]


class Member(TimestampMixin, Base):
    __tablename__ = "member"
    __table_args__ = (
        UniqueConstraint("email", name="email_unique_constraint"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(100))
    roles: Mapped[list[str] | None] = mapped_column(
        ARRAY(String),
        nullable=True,
    )
    translations: Mapped[list[MemberLocale]] = relationship(
        back_populates="member",
        cascade="all, delete-orphan",
    )

    @property
    def name(self) -> str:
        """English given name. Roles and seeds still use this value."""
        return self.text("name")

    def display_name(self, code: str = DEFAULT_CODE) -> str:
        return full_name(self, code) or self.name

    def text(self, field: str, code: str = DEFAULT_CODE) -> str:
        return pick(self, field, code)

    @classmethod
    def ensure(
        cls,
        dbsession: Session,
        email: str,
        name: str,
        *,
        family: str = "",
        translations: dict[str, dict[str, str]] | None = None,
    ) -> Member:
        member = dbsession.scalars(
            select(cls).where(cls.email == email),
        ).first()

        if member is None:
            member = cls(email=email, roles=roles_for(name))
            dbsession.add(member)
            _add_translations(
                member,
                _locales_by_code(dbsession),
                name,
                family,
                translations,
            )

        member.modified_at = utcnow()
        dbsession.flush()
        return member


class MemberLocale(TimestampMixin, Base):
    """Translated name and family for one member in one locale."""

    __tablename__ = "memberlocale"
    __table_args__ = (
        UniqueConstraint(
            "member_id",
            "locale_id",
            name="memberlocale_member_id_locale_id_unique",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    member_id: Mapped[int] = mapped_column(
        ForeignKey("member.id", ondelete="CASCADE"),
    )
    locale_id: Mapped[int] = mapped_column(
        ForeignKey("locale.id"),
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="",
        server_default="",
    )
    family: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="",
        server_default="",
    )

    member: Mapped[Member] = relationship(back_populates="translations")
    locale: Mapped[Locale] = relationship()


def _locales_by_code(dbsession: Session) -> dict[str, Locale]:
    rows = dbsession.scalars(select(Locale)).all()
    return {row.code: row for row in rows}


def _require_locale(locales: dict[str, Locale], code: str) -> Locale:
    locale = locales.get(code)
    if locale is None:
        message = f"unknown locale: {code}"
        raise ValueError(message)
    return locale


def _fields(values: dict[str, str]) -> dict[str, str]:
    unknown = set(values) - set(TEXT_FIELDS)
    if unknown:
        field = sorted(unknown)[0]
        message = f"unknown member text field: {field}"
        raise ValueError(message)
    return {field: values.get(field) or "" for field in TEXT_FIELDS}


def _add_translations(
    member: Member,
    locales: dict[str, Locale],
    name: str,
    family: str,
    translations: dict[str, dict[str, str]] | None,
) -> None:
    member.translations.append(
        MemberLocale(
            locale=_require_locale(locales, DEFAULT_CODE),
            name=name or "",
            family=family or "",
        ),
    )
    for code, values in (translations or {}).items():
        if code == DEFAULT_CODE:
            message = "set the default locale with name and family"
            raise ValueError(message)
        member.translations.append(
            MemberLocale(
                locale=_require_locale(locales, code),
                **_fields(values),
            ),
        )
