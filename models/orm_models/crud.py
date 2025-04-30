from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from marshmallow import Schema
from typing import Type, Any

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


class DBService:
    def __init__(self, model: Type, session: AsyncSession, schema: Type[Schema]):
        self.model = model
        self.session = session
        self.schema = schema()
        self.query = select(model)
        self._executed = False

    def _ensure_not_executed(self):
        """Prevent further chaining after execution"""
        if self._executed:
            raise RuntimeError((
                "Cannot chain further after executing "
                "`all()`, `first()`, or `serialize()`."
            ))

    def where(self, *conditions):
        """Apply WHERE conditions using SQLAlchemy expressions"""
        self._ensure_not_executed()
        self.query = self.query.where(*conditions)
        return self

    def join(self, related_model, condition=None, is_outer=False):
        """Perform INNER JOIN or LEFT JOIN"""
        self._ensure_not_executed()
        if is_outer:
            self.query = self.query.outerjoin(related_model, condition)
        else:
            self.query = self.query.join(related_model, condition)
        return self

    def order_by(self, *args):
        """Order results by specified columns"""
        self._ensure_not_executed()
        self.query = self.query.order_by(*args)
        return self

    def limit(self, count: int):
        """Limit the number of results"""
        self._ensure_not_executed()
        self.query = self.query.limit(count)
        return self

    async def execute(self) -> QueryResultList:
        """Execute the query and return all model instances as a list"""
        self._executed = True
        result = await self.session.execute(self.query)
        obj_list = result.scalars().all()
        return QueryResultList(obj_list, self.schema)  # ✅ Returns a list wrapper

    async def create(self, data: dict, commit: bool) -> QueryResult | None:
        """Create a new record, return the instance, and allow optional serialization"""
        obj = self.model(**data)
        self.session.add(obj)
        if commit:
            await self.session.commit()
            await self.session.refresh(obj)
            return QueryResult(obj, self.schema)

    async def update(self, obj: Any, data: dict, commit: bool) -> QueryResult | None:
        """Update an object instance, refresh it, and allow optional serialization"""
        if not isinstance(obj, self.model):
            raise ValueError("update() requires an instance of the model.")

        for key, value in data.items():
            setattr(obj, key, value)
        if commit:
            await self.session.commit()
            await self.session.refresh(obj)
            return QueryResult(obj, self.schema)

    async def delete(self, obj: Any, commit: bool):
        """Delete an object instance"""
        if not isinstance(obj, self.model):
            raise ValueError("delete() requires an instance of the model.")

        if commit:
            await self.session.delete(obj)
            await self.session.commit()


async def user_list():
    async with (get_session() as session):
        try:
            user_service = DBService(User, session, UserSchema)
            result = (await user_service.where(
                [User.name.like("%omid")]
            )).serialize()
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()

