from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, field_validator


class TestCreateRequest(BaseModel):
    centre_id: str
    name: str
    description: Optional[str] = None
    price: Decimal

    @field_validator("name")
    @classmethod
    def not_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Test name must not be blank")
        return v

    @field_validator("price")
    @classmethod
    def price_positive(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Price must be greater than zero")
        return v


class TestResponse(BaseModel):
    id: str
    centre_id: str
    name: str
    description: Optional[str] = None
    price: Decimal
    created_at: datetime

    model_config = {"from_attributes": True}


class PaginatedTestsResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[TestResponse]
