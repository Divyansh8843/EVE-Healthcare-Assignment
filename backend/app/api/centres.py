from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.diagnostic_centre import DiagnosticCentre
from app.models.user import User
from app.schemas.centre import (
    CentreCreateRequest,
    CentreDetailResponse,
    CentreResponse,
    PaginatedCentresResponse,
)
from app.utils.exceptions import NotFoundError

router = APIRouter(prefix="/centres", tags=["Diagnostic Centres"])


@router.get(
    "",
    response_model=PaginatedCentresResponse,
    summary="List all diagnostic centres",
)
def list_centres(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
):
    skip = (page - 1) * page_size
    query = db.query(DiagnosticCentre)
    total = query.count()
    items = query.order_by(DiagnosticCentre.name).offset(skip).limit(page_size).all()
    return PaginatedCentresResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[CentreResponse.model_validate(c) for c in items],
    )


@router.get(
    "/{centre_id}",
    response_model=CentreDetailResponse,
    summary="Get a single diagnostic centre with its tests",
)
def get_centre(centre_id: str, db: Session = Depends(get_db)):
    centre = db.query(DiagnosticCentre).filter(DiagnosticCentre.id == centre_id).first()
    if not centre:
        raise NotFoundError(f"Diagnostic centre '{centre_id}' not found")
    return CentreDetailResponse.model_validate(centre)


@router.post(
    "",
    response_model=CentreResponse,
    status_code=201,
    summary="Create a diagnostic centre",
    description="Admin operation — no auth required for this demo.",
)
def create_centre(
    payload: CentreCreateRequest,
    db: Session = Depends(get_db),
):
    centre = DiagnosticCentre(name=payload.name, location=payload.location)
    db.add(centre)
    db.commit()
    db.refresh(centre)
    return CentreResponse.model_validate(centre)
