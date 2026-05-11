from math import ceil

from fastapi import Query
from pydantic import BaseModel


class PaginationParams:
    def __init__(
        self,
        skip: int = Query(0, ge=0, description="Number of records to skip"),
        limit: int = Query(100, ge=1, le=500, description="Max records per page"),
    ) -> None:
        self.skip = skip
        self.limit = limit


class PaginatedResponse[T](BaseModel):
    items: list[T]
    total: int
    skip: int
    limit: int

    @property
    def page(self) -> int:
        return (self.skip // self.limit) + 1 if self.limit else 1

    @property
    def pages(self) -> int:
        return max(1, ceil(self.total / self.limit)) if self.limit else 1

    @property
    def has_next(self) -> bool:
        return self.skip + self.limit < self.total

    @property
    def has_prev(self) -> bool:
        return self.skip > 0
