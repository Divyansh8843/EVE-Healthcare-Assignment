from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.booking import (
    BookingCreateRequest,
    BookingCancelResponse,
    BookingResponse,
    PaginatedBookingsResponse,
)
from app.services.booking_service import BookingService

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.post(
    "",
    response_model=BookingResponse,
    status_code=201,
    summary="Create a new booking",
    description=(
        "Authenticated users can book a diagnostic test. "
        "The booking is created in PENDING state; payment must be initiated separately."
    ),
)
def create_booking(
    payload: BookingCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return BookingService(db).create_booking(current_user, payload)


@router.get(
    "",
    response_model=PaginatedBookingsResponse,
    summary="List bookings for the current user",
)
def list_bookings(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return BookingService(db).list_bookings(current_user, page=page, page_size=page_size)


@router.get(
    "/{booking_id}",
    response_model=BookingResponse,
    summary="Get a single booking",
)
def get_booking(
    booking_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return BookingService(db).get_booking(current_user, booking_id)


@router.patch(
    "/{booking_id}/cancel",
    response_model=BookingCancelResponse,
    summary="Cancel a booking",
    description="Cancel a PENDING or CONFIRMED booking. Only the booking owner can cancel.",
)
def cancel_booking(
    booking_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return BookingService(db).cancel_booking(current_user, booking_id)
