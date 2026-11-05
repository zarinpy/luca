from luca.database import Database

from .auth import basedata as auth_basedata
from .site import basedata as site_basedata


def insert(db: Database) -> None:
    print(f"generate base data, db url: {db.engine.url}")
    auth_basedata.insert(db)
    site_basedata.insert(db)
