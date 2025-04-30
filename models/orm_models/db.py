import uuid
from contextvars import ContextVar

import sqlalchemy
from sqlalchemy import Column, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, declarative_base
from setting import setting
db_session_var: ContextVar[AsyncSession | None] = ContextVar("db_session", default=None)


# Create an async async_engine
async_engine = create_async_engine(
    setting.DB_URI,
    echo=False,  # Disable SQLAlchemy echoing queries (useful in production)
    pool_size=20,  # Max number of connections in the pool
    max_overflow=10,  # Allow 10 extra connections beyond the pool_size
    pool_timeout=30,  # Wait time (seconds) for a connection from the pool before raising an error
    pool_recycle=1800,  # Recycle connections every 30 minutes (prevents stale connections)
)
async_session = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def check_pool_status(s):
    # # Retrieve the connection pool object from the session engine
    pool = (await s.connection()).engine.pool

    # Get the number of checked-out connections
    checked_out_connections = pool.checkedout()
    # Get the number of available connections
    available_connections = pool.size() - checked_out_connections
    # Get the total number of connections
    total_connections = pool.size()

    print(f"Checked-out connections (active sessions): {checked_out_connections}")
    print(f"Available connections: {available_connections}")
    print(f"Total connections: {total_connections}")

async def session() -> AsyncSession:
    async with async_session() as s:
        try:
            yield s
        except Exception as e:
            # Handle exceptions (e.g., rollback)
            await s.rollback()
            raise
        finally:
            # print("session closed")
            await s.close()

# Define your base class for models
metadata = sqlalchemy.MetaData()
