from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.booking import Booking, BookingStatus
from app.models.diagnostic_centre import DiagnosticCentre
from app.models.diagnostic_test import DiagnosticTest
from app.models.user import User
from app.repositories.booking_repository import BookingRepository
from app.schemas.booking import (
    BookingCreateRequest,
    BookingResponse,
    BookingCancelResponse,
    PaginatedBookingsResponse,
)
from app.utils.exceptions import (
    BadRequestError,
    ForbiddenError,
    NotFoundError,
    UnprocessableError,
)
from app.utils.logging import get_logger

logger = get_logger(__name__)


class BookingService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = BookingRepository(db)

    def create_booking(self, user: User, payload: BookingCreateRequest) -> BookingResponse:
        """Create a new booking in PENDING state.

        Validates that:
        - The test exists
        - The centre exists
        - The test belongs to the specified centre
        """
        # Validate test
        test: DiagnosticTest | None = (
            self.db.query(DiagnosticTest)
            .filter(DiagnosticTest.id == payload.test_id)
            .first()
        )
        if not test:
            raise NotFoundError(f"Diagnostic test '{payload.test_id}' not found")

        # Validate centre
        centre: DiagnosticCentre | None = (
            self.db.query(DiagnosticCentre)
            .filter(DiagnosticCentre.id == payload.centre_id)
            .first()
        )
        if not centre:
            raise NotFoundError(f"Diagnostic centre '{payload.centre_id}' not found")

        # Ensure the test belongs to the stated centre
        if test.centre_id != centre.id:
            raise BadRequestError(
                f"Test '{test.name}' does not belong to centre '{centre.name}'"
            )

        booking = self.repo.create(
            user_id=user.id,
            test_id=test.id,
            centre_id=centre.id,
            appointment_time=payload.appointment_time,
            amount=test.price,
        )
        self.db.commit()
        self.db.refresh(booking)

        logger.info(
            "booking_created",
            booking_id=booking.id,
            user_id=user.id,
            amount=str(booking.amount),
        )
        return BookingResponse.model_validate(booking)

    def get_booking(self, user: User, booking_id: str) -> BookingResponse:
        """Retrieve a booking; only the owner can view it."""
        booking = self._get_owned_booking(user, booking_id)
        return BookingResponse.model_validate(booking)

    def list_bookings(
        self, user: User, page: int = 1, page_size: int = 20
    ) -> PaginatedBookingsResponse:
        skip = (page - 1) * page_size
        total, items = self.repo.list_by_user(user.id, skip=skip, limit=page_size)
        return PaginatedBookingsResponse(
            total=total,
            page=page,
            page_size=page_size,
            items=[BookingResponse.model_validate(b) for b in items],
        )

    def cancel_booking(self, user: User, booking_id: str) -> BookingCancelResponse:
        """Cancel a PENDING or CONFIRMED booking.

        Rules:
        - Only the owner can cancel.
        - Only PENDING or CONFIRMED bookings can be cancelled.
        """
        booking = self._get_owned_booking(user, booking_id)

        if booking.status == BookingStatus.CANCELLED:
            raise BadRequestError("Booking is already cancelled")

        if booking.status == BookingStatus.FAILED:
            raise UnprocessableError("Cannot cancel a failed booking")

        self.repo.update_status(booking, BookingStatus.CANCELLED)
        self.db.commit()

        logger.info("booking_cancelled", booking_id=booking.id, user_id=user.id)
        return BookingCancelResponse(
            id=booking.id,
            status=BookingStatus.CANCELLED,
            message="Booking cancelled successfully",
        )

    def _get_owned_booking(self, user: User, booking_id: str) -> Booking:
        """Fetch a booking and enforce ownership."""
        booking = self.repo.get_by_id(booking_id)
        if not booking:
            raise NotFoundError(f"Booking '{booking_id}' not found")
        if booking.user_id != user.id:
            raise ForbiddenError("You do not have permission to access this booking")
        return booking
