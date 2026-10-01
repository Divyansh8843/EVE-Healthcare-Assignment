from typing import Optional

from sqlalchemy.orm import Session

from app.models.payment import Payment, PaymentStatus


class PaymentRepository:
    """Data-access layer for Payment objects."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_event_id(self, event_id: str) -> Optional[Payment]:
        """Look up a payment by its idempotency event_id."""
        return self.db.query(Payment).filter(Payment.event_id == event_id).first()

    def get_by_id(self, payment_id: str) -> Optional[Payment]:
        return self.db.query(Payment).filter(Payment.id == payment_id).first()

    def get_by_booking_id(self, booking_id: str) -> list[Payment]:
        return (
            self.db.query(Payment)
            .filter(Payment.booking_id == booking_id)
            .order_by(Payment.created_at.desc())
            .all()
        )

    def create(
        self,
        booking_id: str,
        event_id: str,
        amount,
        status: PaymentStatus,
    ) -> Payment:
        payment = Payment(
            booking_id=booking_id,
            event_id=event_id,
            amount=amount,
            status=status,
        )
        self.db.add(payment)
        self.db.flush()
        return payment
