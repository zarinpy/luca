from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from luca.common.models import Base, TimestampMixin

SINGLETON_ID = 1

DEFAULTS = {
    "name": "Luca",
    "email": "",
}


class SiteSettings(TimestampMixin, Base):
    __tablename__ = "sitesettings"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(
        String(256),
        nullable=False,
        default="",
    )
