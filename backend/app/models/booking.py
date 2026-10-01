import uuid
import enum
from datetime import datetime
from decimal import Decimal

from sqlalchemy import String, DateTime, Numeric, ForeignKey, Enum as SAEnum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class BookingStatus(str, enum.Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    test_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("diagnostic_tests.id", ondelete="RESTRICT"), nullable=False
    )
    centre_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("diagnostic_centres.id", ondelete="RESTRICT"), nullable=False
    )
    appointment_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[BookingStatus] = mapped_column(
        SAEnum(BookingStatus, name="bookingstatus"), nullable=False, default=BookingStatus.PENDING
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship("User")  # noqa: F821
    test: Mapped["DiagnosticTest"] = relationship("DiagnosticTest")  # noqa: F821
    centre: Mapped["DiagnosticCentre"] = relationship("DiagnosticCentre")  # noqa: F821
    payments: Mapped[list["Payment"]] = relationship(  # noqa: F821
        "Payment", back_populates="booking"
    )

    def __repr__(self) -> str:
        return f"<Booking id={self.id} status={self.status}>"
