from __future__ import annotations

from sqlalchemy import String, UniqueConstraint, select
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, Session, mapped_column

from luca.common.datetime import utcnow
from luca.common.models import Base, TimestampMixin

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
    name: Mapped[str | None] = mapped_column(String(30))
    roles: Mapped[list[str] | None] = mapped_column(
        ARRAY(String),
        nullable=True,
    )

    @classmethod
    def ensure(
        cls,
        dbsession: Session,
        email: str,
        name: str,
    ) -> Member:
        member = dbsession.scalars(
            select(cls).where(cls.email == email),
        ).first()

        if member is None:
            member = cls(
                email=email,
                name=name,
                roles=roles_for(name),
            )
            dbsession.add(member)

        member.modified_at = utcnow()
        dbsession.flush()
        return member
