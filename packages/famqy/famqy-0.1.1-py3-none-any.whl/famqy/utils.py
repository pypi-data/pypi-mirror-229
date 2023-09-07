from enum import Enum

from pydantic import BaseModel


class Operations(Enum):
    GT = '{"$gt": replacement}'
    GTE = '{"$gte": replacement}'
    LT = '{field: {"$lt": replacement}'
    LTE = '{"$lte": replacement}'
    EQ = '{"$eq": replacement}'
    NE = '{"$ne": replacement}'
    STARTSWITH = '{"$regex": f"^{replacement}[\\s\\S]*"}'
    ENDSWITH = '{"$regex": f"[\\s\\S]*?{replacement}$"}'
    CONTAINS = "replacement"
    IN = '{"$in": replacement}'
    MATCH = '{"$regex": replacement}'


class Sort(BaseModel):
    field: str
    order: int


class Pagination(BaseModel):
    offset: int | None
    limit: int | None
    sort: list[Sort]


class SortConfig(BaseModel):
    config: dict
    values: list[str]
