from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, field_validator


# ---- Nested test schema (used inside centre response) ----

class TestInCentreResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    price: Decimal

    model_config = {"from_attributes": True}


# ---- Centre schemas ----

class CentreCreateRequest(BaseModel):
    name: str
    location: str

    @field_validator("name", "location")
    @classmethod
    def not_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Field must not be blank")
        return v


class CentreResponse(BaseModel):
    id: str
    name: str
    location: str
    created_at: datetime

    model_config = {"from_attributes": True}


class CentreDetailResponse(BaseModel):
    id: str
    name: str
    location: str
    created_at: datetime
    tests: list[TestInCentreResponse] = []

    model_config = {"from_attributes": True}


class PaginatedCentresResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[CentreResponse]
