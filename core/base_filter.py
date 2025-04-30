from typing import Type

from pydantic import BaseModel
from sqlalchemy.orm import Query
from sqlalchemy.sql import operators

operator_map = {
            "__eq": operators.eq,
            "__lt": operators.lt,
            "__lte": operators.le,
            "__gt": operators.gt,
            "__gte": operators.ge,
            "__icontains": lambda col, val: col.ilike(f"%{val}%"),
            "__startswith": lambda col, val: col.ilike(f"{val}%"),
            "__endswith": lambda col, val: col.ilike(f"%{val}"),
            "__not_startswith": lambda col, val: ~col.ilike(f"{val}%"),
            "__not_endswith": lambda col, val: ~col.ilike(f"%{val}"),
        }


class BaseFilter(BaseModel):
    """
    A base class for creating Django-like filters with operators.
    """

    def apply_filters(self, query: Query, model: Type) -> Query:
        """
        Dynamically apply filters with operator support.
        """

        for field, value in self.model_dump(exclude_none=True).items():
            parts = field.split("__")  # Split by operator suffix
            column_name = parts[0]
            operator_suffix = f"__{parts[1]}" if len(parts) > 1 else "__eq"

            if hasattr(model, column_name) and operator_suffix in operator_map:
                column = getattr(model, column_name)
                operator_fn = operator_map[operator_suffix]
                query = query.filter(operator_fn(column, value))
        return query
