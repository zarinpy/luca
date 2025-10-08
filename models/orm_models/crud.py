from __future__ import annotations

from typing import TYPE_CHECKING, Any, Self

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

from fastapi.exceptions import HTTPException
from sqlalchemy import select, update
from sqlalchemy.exc import MultipleResultsFound

__all__ = ["CRUD"]

from starlette import status


class QueryResult:

    def __init__(self, obj, schema):   #noqa: ANN001 ANN204
        self.obj = obj
        self.schema = schema
        self._executed = False

    def __getattr__(self, item):   #noqa: ANN001 ANN204
        return getattr(self.obj, item)

    def __repr__(self) -> str:
        return f"{self.obj}"

    def serialize(self):   # noqa: ANN202
        """Convert object to a dictionary using Marshmallow"""
        if self._executed:
            msg = "Cannot call `.serialize()` multiple times."
            raise RuntimeError(msg)
        self._executed = True
        return self.schema.dump(self.obj) if self.obj else None


class QueryResultList:

    def __init__(self, obj_list, schema):   # noqa: ANN001 ANN204
        self.obj_list = obj_list
        self.schema = schema
        self._executed = False

    def serialize(self):  # noqa: ANN202
        if self._executed:
            msg = "Cannot call `.serialize()` multiple times."
            raise RuntimeError(msg)
        self._executed = True
        return self.schema.dump(self.obj_list, many=True)

    def __iter__(self):    # noqa: ANN204
        """Allow iteration over the list"""
        return iter(self.obj_list)

    def __getitem__(self, index):   # noqa: ANN001, ANN204
        """Allow index-based access"""
        return self.obj_list[index]

    def __len__(self) -> int:
        """Return length of list"""
        return len(self.obj_list)

    def __repr__(self) -> str:
        return f"{self.obj_list}"


class CRUD:

    @classmethod
    async def get_or_create(
            cls,
            session: AsyncSession,
            keys: dict[str, Any],
            defaults: dict[str, Any],
    ) -> Self:
        obj = await cls.get(session, keys)

        if obj is None:
            obj = await cls.create(session, data=defaults)

        return obj

    @classmethod
    async def get(
            cls,
            session: AsyncSession,
            keys: dict[str, Any],
            *,
            raise_exception: bool = False,
    ) -> Self:
        result = (
            await session.execute(
                select(cls).filter_by(**keys))
        ).unique().scalars().all()

        if len(result) > 1:
            detail = f"multiple results found for: {keys}"
            raise MultipleResultsFound(detail=detail)
        if not result:
            if raise_exception:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Item not found",
                )
            return None

        return result[0]

    @classmethod
    async def create(
            cls,
            session: AsyncSession,
            data: dict[str, Any],
    ) -> Self:
        obj = cls(**data)
        session.add(obj)
        await session.commit()
        await session.refresh(obj)
        return obj

    async def delete(self, session: AsyncSession) -> None:
        await session.delete(self)
        await session.commit()

    async def update(self, session: AsyncSession, data: dict) -> None:
        await session.execute(
            update(self.__class__)
            .where(self.__class__.id == self.id)
            .values(**data),
        )
        await session.commit()
