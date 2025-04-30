from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from models.orm_models.db import session
__all__ = ["DBSession"]


DBSession = Annotated[AsyncSession, Depends(session)]