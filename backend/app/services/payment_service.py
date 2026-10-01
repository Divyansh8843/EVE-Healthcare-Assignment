import random
import uuid

from sqlalchemy.orm import Session

from app.models.booking import Booking, BookingStatus
from app.models.payment import PaymentStatus
from app.models.user import User
from app.repositories.booking_repository import BookingRepository
from app.repositories.payment_repository import PaymentRepository
from app.schemas.payment import PaymentInitiateRequest, PaymentResponse, WebhookPayload, WebhookResponse
from app.utils.exceptions import BadRequestError, NotFoundError, ForbiddenError
from app.utils.logging import get_logger

logger = get_logger(__name__)

# Simulated success probability (70% success, 30% failure)
_SUCCESS_PROBABILITY = 0.7


class PaymentService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.booking_repo = BookingRepository(db)
        self.payment_repo = PaymentRepository(db)

    def initiate_payment(self, user: User, payload: PaymentInitiateRequest) -> PaymentResponse:
        """Simulate a payment for a PENDING booking.

        The outcome (SUCCESS / FAILED) is randomly determined and both the
        Payment record and Booking status are updated atomically.
        """
        booking = self.booking_repo.get_by_id(payload.booking_id)
        if not booking:
            raise NotFoundError(f"Booking '{payload.booking_id}' not found")
        if booking.user_id != user.id:
            raise ForbiddenError("You do not own this booking")
        if booking.status != BookingStatus.PENDING:
            raise BadRequestError(
                f"Only PENDING bookings can be paid. Current status: {booking.status}"
            )

        # Simulate payment outcome
        outcome = PaymentStatus.SUCCESS if random.random() < _SUCCESS_PROBABILITY else PaymentStatus.FAILED
        event_id = str(uuid.uuid4())   # Internal event ID for this simulated payment

        # --- Atomic transaction ---
        try:
            payment = self.payment_repo.create(
                booking_id=booking.id,
                event_id=event_id,
                amount=booking.amount,
                status=outcome,
            )
            new_booking_status = (
                BookingStatus.CONFIRMED if outcome == PaymentStatus.SUCCESS else BookingStatus.FAILED
            )
            self.booking_repo.update_status(booking, new_booking_status)
            self.db.commit()
            self.db.refresh(payment)
        except Exception:
            self.db.rollback()
            raise

        logger.info(
            "payment_processed",
            payment_id=payment.id,
            booking_id=booking.id,
            outcome=outcome,
        )
        return PaymentResponse.model_validate(payment)

    def get_payment(self, user: User, payment_id: str) -> PaymentResponse:
        payment = self.payment_repo.get_by_id(payment_id)
        if not payment:
            raise NotFoundError(f"Payment '{payment_id}' not found")
        # Ensure the requesting user owns the linked booking
        if payment.booking.user_id != user.id:
            raise ForbiddenError("You do not have permission to view this payment")
        return PaymentResponse.model_validate(payment)

    def handle_webhook(self, payload: WebhookPayload) -> WebhookResponse:
        """Process a payment webhook idempotently.

        Algorithm:
        1. Check if a Payment with this event_id already exists.
           - If yes → return 200 immediately (idempotent no-op).
        2. Validate the referenced Booking.
        3. Create the Payment and update Booking status in one transaction.

        The UNIQUE constraint on ``payments.event_id`` is a final safety net
        in case two concurrent requests with the same event_id slip through
        step 1 simultaneously.
        """
        existing = self.payment_repo.get_by_event_id(payload.event_id)
        if existing:
            logger.info(
                "webhook_duplicate_ignored",
                event_id=payload.event_id,
                payment_id=existing.id,
            )
            return WebhookResponse(
                received=True,
                event_id=payload.event_id,
                message="Event already processed (idempotent response)",
            )

        # Validate booking
        booking = self.booking_repo.get_by_id(payload.booking_id)
        if not booking:
            raise NotFoundError(f"Booking '{payload.booking_id}' not found")

        # Only process webhooks for bookings that are still PENDING.
        # CONFIRMED / FAILED / CANCELLED are terminal — reject any further webhook.
        if booking.status != BookingStatus.PENDING:
            raise BadRequestError(
                f"Booking is in state '{booking.status}' and cannot be updated via webhook"
            )

        # --- Atomic transaction ---
        try:
            self.payment_repo.create(
                booking_id=booking.id,
                event_id=payload.event_id,
                amount=payload.amount,
                status=payload.status,
            )
            new_status = (
                BookingStatus.CONFIRMED
                if payload.status == PaymentStatus.SUCCESS
                else BookingStatus.FAILED
            )
            self.booking_repo.update_status(booking, new_status)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

        logger.info(
            "webhook_processed",
            event_id=payload.event_id,
            booking_id=booking.id,
            payment_status=payload.status,
            new_booking_status=new_status,
        )
        return WebhookResponse(
            received=True,
            event_id=payload.event_id,
            message=f"Webhook processed. Booking updated to {new_status}",
        )
