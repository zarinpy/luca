from luca.database import Database

from .auth import mockup as auth_mockup


def insert(db: Database) -> None:
    print(f"generating mockup data, db url: {db.engine.url}")
    auth_mockup.insert(db)
    print("mockup data generation done")
