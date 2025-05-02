from typing import Any, Dict, List

from fastapi import HTTPException
from sqlalchemy import CursorResult, Result, select, update
from sqlalchemy.exc import MultipleResultsFound
from sqlalchemy.ext.asyncio import AsyncSession

__all__ = ["CRUD"]

from starlette import status


class QueryResult:
    """Wrapper class to allow optional serialization of a single instance"""
    def __init__(self, obj, schema):
        self.obj = obj
        self.schema = schema
        self._executed = False

    def __getattr__(self, item):
        """Allow direct access to instance attributes"""
        return getattr(self.obj, item)

    def __repr__(self):
        return f"{self.obj}"

    def serialize(self):
        """Convert object to a dictionary using Marshmallow"""
        if self._executed:
            raise RuntimeError("Cannot call `.serialize()` multiple times.")
        self._executed = True
        return self.schema.dump(self.obj) if self.obj else None


class QueryResultList:
    """Wrapper class to allow optional serialization of a list of instances"""
    def __init__(self, obj_list, schema):
        self.obj_list = obj_list
        self.schema = schema
        self._executed = False

    def serialize(self):
        """Convert list of objects to a list of dictionaries using Marshmallow"""
        if self._executed:
            raise RuntimeError("Cannot call `.serialize()` multiple times.")
        self._executed = True
        return self.schema.dump(self.obj_list, many=True)

    def __iter__(self):
        """Allow iteration over the list"""
        return iter(self.obj_list)

    def __getitem__(self, index):
        """Allow index-based access"""
        return self.obj_list[index]

    def __len__(self):
        """Return length of list"""
        return len(self.obj_list)

    def __repr__(self):
        return f"{self.obj_list}"


class CRUD:

    @classmethod
    async def get_or_create(
            cls,
            session: AsyncSession,
            keys: Dict[str, Any],
            defaults: Dict[str, Any],
    ):
        obj = await cls.get(session, keys)

        if obj is None:
            obj = await cls.create(session, data=defaults)

        return obj

    # TODO need latest record
    @classmethod
    async def get(
            cls,
            session: AsyncSession,
            keys: Dict[str, Any],
            raise_exception: bool = False
    ):
        result = (
            await session.execute(
                select(cls).filter_by(**keys))
        ).unique().scalars().all()

        if len(result) > 1:
            raise MultipleResultsFound(
                f"multiple results found for: {keys}"
            )
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
            data: Dict[str, Any],
    ) -> Any:
        """create a single entity with given data"""
        obj = cls(**data)
        session.add(obj)
        await session.commit()
        await session.refresh(obj)
        return obj

    async def delete(self, session: AsyncSession):
        await session.delete(self)
        await session.commit()

    async def update(self, session: AsyncSession, data: Dict):
        await session.execute(
            update(self.__class__)
            .where(self.__class__.id == self.id)
            .values(**data)
        )
        await session.commit()

    @classmethod
    async def update_or_create(
            cls,
            session: AsyncSession,
            defaults: Dict[str, Any],
            create_defaults: Dict[str, Any],
            **kwargs
    ) -> Result[Any] | CursorResult[Any]:
        raise NotImplementedError

    @classmethod
    async def bulk_create(
            cls,
            session: AsyncSession,
            data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """bulk insert to db"""
        raise NotImplementedError

    @classmethod
    async def bulk_update(cls, session: AsyncSession,
                          filters: Dict[str, Any],
                          data: List[Dict[str, Any]]) -> int:
        """bulk update into db return affected rows"""
        raise NotImplementedError

    @classmethod
    async def bulk_delete(
            cls,
            session: AsyncSession,
            filters: Dict[str, Any],
            data: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """delete multiple entities from db"""
        raise NotImplementedError
