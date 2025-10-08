import sqlalchemy
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from setting import setting

# Create an async async_engine
async_engine = create_async_engine(
    setting.DB_URI,
# Disable SQLAlchemy echoing queries (useful in production)
    echo=False,
# Max number of connections in the pool
    pool_size=20,
# Allow 10 extra connections beyond the pool_size
    max_overflow=10,
# Wait time (seconds) for a connection from the pool before raising an error
    pool_timeout=30,
# Recycle connections every 30 minutes (prevents stale connections)
    pool_recycle=1800,
)
async_session = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def session() -> AsyncSession:
    async with async_session() as s:
        try:
            yield s
        except Exception:
            # Handle exceptions (e.g., rollback)
            await s.rollback()
            raise
        finally:
            await s.close()

# Define your base class for models
metadata = sqlalchemy.MetaData()
