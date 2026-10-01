from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.payment import (
    PaymentInitiateRequest,
    PaymentResponse,
    WebhookPayload,
    WebhookResponse,
)
from app.services.payment_service import PaymentService

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post(
    "",
    response_model=PaymentResponse,
    status_code=201,
    summary="Initiate a simulated payment",
    description=(
        "Simulates payment processing for a PENDING booking. "
        "The outcome (SUCCESS / FAILED) is randomly determined (70% success). "
        "The booking status is updated atomically."
    ),
)
def initiate_payment(
    payload: PaymentInitiateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return PaymentService(db).initiate_payment(current_user, payload)


@router.get(
    "/{payment_id}",
    response_model=PaymentResponse,
    summary="Get a payment by ID",
)
def get_payment(
    payment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return PaymentService(db).get_payment(current_user, payment_id)


@router.post(
    "/webhook",
    response_model=WebhookResponse,
    summary="Payment webhook (idempotent)",
    description=(
        "Accepts payment status updates from the simulated payment provider. "
        "The same event_id may be delivered multiple times — duplicate events "
        "are silently ignored and a 200 is returned (idempotent behaviour)."
    ),
)
def payment_webhook(payload: WebhookPayload, db: Session = Depends(get_db)):
    """No auth required — webhook calls come from the payment provider, not users."""
    return PaymentService(db).handle_webhook(payload)
