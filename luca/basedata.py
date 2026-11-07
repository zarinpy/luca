from luca.database import Database

from .auth import basedata as auth_basedata
from .locale import basedata as locale_basedata


def insert(db: Database) -> None:
    print(f"generate base data, db url: {db.engine.url}")
    locale_basedata.insert(db)
    auth_basedata.insert(db)
