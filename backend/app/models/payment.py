import uuid
import enum
from datetime import datetime
from decimal import Decimal

from sqlalchemy import String, DateTime, Numeric, ForeignKey, Enum as SAEnum, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class PaymentStatus(str, enum.Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class Payment(Base):
    """Represents one payment attempt linked to a Booking.

    ``event_id`` is used for idempotency: the same webhook event must never
    create a second Payment row.  The UNIQUE constraint at the DB level is the
    last line of defence after the application-level check.
    """

    __tablename__ = "payments"

    # Unique constraint on event_id ensures webhook idempotency at DB level
    __table_args__ = (
        UniqueConstraint("event_id", name="uq_payments_event_id"),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    booking_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("bookings.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    # event_id is a stable identifier provided by the payment provider
    # (or generated internally for direct POST /payments/).
    # Its UNIQUE constraint is what makes the webhook idempotent.
    event_id: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[PaymentStatus] = mapped_column(
        SAEnum(PaymentStatus, name="paymentstatus"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    booking: Mapped["Booking"] = relationship("Booking", back_populates="payments")  # noqa: F821

    def __repr__(self) -> str:
        return f"<Payment id={self.id} event_id={self.event_id} status={self.status}>"
