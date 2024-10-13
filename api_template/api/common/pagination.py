from typing import Generic, List, TypeVar

from fastapi import Query
from pydantic import BaseModel

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    size: int
    pages: int

    class Config:
        arbitrary_types_allowed = True


class Paginator:
    def __init__(self, page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=100)):
        self.page = page
        self.size = size


def paginate(items: List[T], paginator: Paginator, total: int) -> Page[T]:
    return Page(
        items=items,
        total=total,
        page=paginator.page,
        size=paginator.size,
        pages=(total + paginator.size - 1) // paginator.size,
    )
