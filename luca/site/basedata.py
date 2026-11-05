from luca.database import Database

from .models import DEFAULTS, SINGLETON_ID, SiteSettings


def insert(db: Database) -> None:
    with db.session() as session:
        if session.get(SiteSettings, SINGLETON_ID) is not None:
            return
        session.add(SiteSettings(id=SINGLETON_ID, **DEFAULTS))
        session.commit()
