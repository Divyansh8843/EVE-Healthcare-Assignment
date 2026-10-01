from typing import Optional

from sqlalchemy.orm import Session, joinedload

from app.models.booking import Booking, BookingStatus


class BookingRepository:
    """Data-access layer for Booking objects."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, booking_id: str) -> Optional[Booking]:
        """Fetch a booking with test and centre eagerly loaded."""
        return (
            self.db.query(Booking)
            .options(joinedload(Booking.test), joinedload(Booking.centre))
            .filter(Booking.id == booking_id)
            .first()
        )

    def get_by_id_with_relations(self, booking_id: str) -> Optional[Booking]:
        """Fetch a booking with all relations (user, test, centre) eagerly loaded."""
        return (
            self.db.query(Booking)
            .options(
                joinedload(Booking.user),
                joinedload(Booking.test),
                joinedload(Booking.centre),
            )
            .filter(Booking.id == booking_id)
            .first()
        )

    def list_by_user(
        self, user_id: str, skip: int = 0, limit: int = 20
    ) -> tuple[int, list[Booking]]:
        query = self.db.query(Booking).filter(Booking.user_id == user_id)
        total = query.count()
        items = (
            query
            .options(joinedload(Booking.test), joinedload(Booking.centre))
            .order_by(Booking.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return total, items

    def create(
        self,
        user_id: str,
        test_id: str,
        centre_id: str,
        appointment_time,
        amount,
    ) -> Booking:
        booking = Booking(
            user_id=user_id,
            test_id=test_id,
            centre_id=centre_id,
            appointment_time=appointment_time,
            amount=amount,
            status=BookingStatus.PENDING,
        )
        self.db.add(booking)
        self.db.flush()
        return booking

    def update_status(self, booking: Booking, status: BookingStatus) -> Booking:
        booking.status = status
        self.db.flush()
        return booking
