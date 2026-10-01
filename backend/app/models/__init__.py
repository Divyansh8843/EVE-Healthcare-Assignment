# Import all models here so Alembic can discover them via Base.metadata
from app.models.user import User
from app.models.diagnostic_centre import DiagnosticCentre
from app.models.diagnostic_test import DiagnosticTest
from app.models.booking import Booking, BookingStatus
from app.models.payment import Payment, PaymentStatus

__all__ = [
    "User",
    "DiagnosticCentre",
    "DiagnosticTest",
    "Booking",
    "BookingStatus",
    "Payment",
    "PaymentStatus",
]
