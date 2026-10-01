"""EVE Healthcare — Diagnostic Booking & Payment Backend.

Entry point for the FastAPI application.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import auth, bookings, centres, payments, tests
from app.core.config import settings
from app.core.database import Base, engine
from app.utils.exceptions import (
    BadRequestError,
    ConflictError,
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
    UnprocessableError,
)
from app.utils.logging import configure_logging, get_logger

configure_logging()
logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Lifespan: create tables on startup (Alembic preferred for production)
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Import all models so Base.metadata knows about them
    import app.models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    logger.info("startup_complete", version=settings.VERSION)
    yield
    logger.info("shutdown")


# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "Backend service for diagnostic test bookings and simulated payments. "
        "Built with FastAPI + PostgreSQL for the EVE Healthcare SDE Intern Assignment."
    ),
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(auth.router)
app.include_router(centres.router)
app.include_router(tests.router)
app.include_router(bookings.router)
app.include_router(payments.router)


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
@app.get("/health", tags=["Health"], summary="Service health check")
def health():
    return {"status": "ok", "version": settings.VERSION}


# ---------------------------------------------------------------------------
# Global exception handlers (catch-all for unexpected errors)
# ---------------------------------------------------------------------------
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error(
        "unhandled_exception",
        path=request.url.path,
        method=request.method,
        error=str(exc),
        exc_info=True,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred. Please try again later."},
    )
