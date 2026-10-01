from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel

from app.models.payment import PaymentStatus


class PaymentInitiateRequest(BaseModel):
    """Client sends this to POST /payments/ to initiate a simulated payment."""
    booking_id: str


class PaymentResponse(BaseModel):
    id: str
    booking_id: str
    event_id: str
    amount: Decimal
    status: PaymentStatus
    created_at: datetime

    model_config = {"from_attributes": True}


class WebhookPayload(BaseModel):
    """Payload shape expected from the simulated payment provider.

    ``event_id`` is the idempotency key — the provider may retry delivery,
    but the same event_id must only be processed once.
    """
    event_id: str
    booking_id: str
    status: PaymentStatus
    amount: Decimal


class WebhookResponse(BaseModel):
    received: bool
    event_id: str
    message: str
