from luca.common.datetime import utcnow
from luca.database import Database

BUILTIN_USERS = [
    "God",
    "Admin",
]

GODS = ["God", "Vahid", "Pylover"]
ADMINS = ["Admin"]


def ensure_members(
    db: Database,
    members: list[tuple[str, str]],
) -> None:
    from . import models

    with db.session() as session:
        for name, email in members:
            print(f"Creating member: {name}")
            member = models.Member.ensure(session, email, name)

            # freezegun issue
            member.created_at = utcnow()
            session.add(member)
            session.commit()


def insert(db: Database) -> None:
    print("generating authentication module's base data")
    ensure_members(
        db,
        [(name, f"{name.lower()}@example.com") for name in BUILTIN_USERS],
    )
