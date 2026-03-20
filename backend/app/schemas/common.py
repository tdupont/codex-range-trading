from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, Field
from pydantic.generics import GenericModel


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: dict[str, str | int | float | None] | None = None


class ErrorResponse(BaseModel):
    error: ErrorDetail


class Pagination(BaseModel):
    page: int
    page_size: int
    total_items: int
    total_pages: int


T = TypeVar("T")


class PaginatedResponse(GenericModel, Generic[T]):
    data: list[T]
    pagination: Pagination
