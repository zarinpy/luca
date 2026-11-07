from sqlalchemy import select

from luca.database import Database
from luca.i18n import LOCALES

from .models import Locale


def insert(db: Database) -> None:
    print("generating locale module's base data")
    with db.session() as session:
        present = {
            row.code for row in session.scalars(select(Locale)).all()
        }
        for name, code in LOCALES:
            if code in present:
                continue
            print(f"Creating locale: {code}")
            session.add(Locale(code=code, name=name))
            present.add(code)
        session.commit()
