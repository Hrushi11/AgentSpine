"""Helpers to serialize ORM rows and SDK models for HTTP responses."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel
from sqlalchemy.inspection import inspect


def to_jsonable(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json")
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {key: to_jsonable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [to_jsonable(item) for item in value]
    return value


def serialize_model(row: Any) -> dict[str, Any]:
    mapper = inspect(row)
    return {attr.key: to_jsonable(getattr(row, attr.key)) for attr in mapper.mapper.column_attrs}
