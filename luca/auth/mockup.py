from luca.database import Database

from .basedata import ensure_members

USERS = [
    ("bob", "bob@example.com"),
    ("alice", "alice@example.com"),
]


def insert(db: Database) -> None:
    print("generating authentication module's mockup data")
    ensure_members(
        db,
        [(name.capitalize(), email) for name, email in USERS],
    )
