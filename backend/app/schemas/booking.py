from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, field_validator, model_validator

from app.models.booking import BookingStatus


class BookingCreateRequest(BaseModel):
    test_id: str
    centre_id: str
    appointment_time: datetime

    @field_validator("appointment_time")
    @classmethod
    def appointment_must_be_future(cls, v: datetime) -> datetime:
        from datetime import timezone
        now = datetime.now(timezone.utc)
        # Ensure tz-aware comparison
        if v.tzinfo is None:
            raise ValueError("appointment_time must include timezone information (e.g. 2026-10-05T10:00:00+05:30)")
        if v <= now:
            raise ValueError("Appointment time must be in the future")
        return v


class BookingResponse(BaseModel):
    id: str
    user_id: str
    test_id: str
    centre_id: str
    appointment_time: datetime
    amount: Decimal
    status: BookingStatus
    created_at: datetime

    # Enriched fields — populated from ORM relationships
    test_name: Optional[str] = None
    centre_name: Optional[str] = None
    test_description: Optional[str] = None
    centre_location: Optional[str] = None

    model_config = {"from_attributes": True}

    @model_validator(mode="before")
    @classmethod
    def populate_nested(cls, values):
        """Pull names from ORM relationships when building from ORM objects."""
        # When values is an ORM model instance (not a dict), read attributes
        if not isinstance(values, dict):
            obj = values
            try:
                if obj.test:
                    values = {
                        **{k: getattr(obj, k) for k in [
                            "id", "user_id", "test_id", "centre_id",
                            "appointment_time", "amount", "status", "created_at"
                        ]},
                        "test_name": obj.test.name,
                        "test_description": getattr(obj.test, "description", None),
                        "centre_name": obj.centre.name if obj.centre else None,
                        "centre_location": obj.centre.location if obj.centre else None,
                    }
            except Exception:
                pass
        return values


class BookingCancelResponse(BaseModel):
    id: str
    status: BookingStatus
    message: str


class PaginatedBookingsResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[BookingResponse]
