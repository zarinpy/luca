from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from luca.common.models import Base, TimestampMixin


class Locale(TimestampMixin, Base):
    """One supported locale, such as `en-US` or `fa-IR`."""

    __tablename__ = "locale"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(16), unique=True)
    name: Mapped[str] = mapped_column(String(64))
