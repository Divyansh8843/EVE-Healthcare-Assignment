from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.diagnostic_centre import DiagnosticCentre
from app.models.diagnostic_test import DiagnosticTest
from app.schemas.test import TestCreateRequest, TestResponse, PaginatedTestsResponse
from app.utils.exceptions import NotFoundError

router = APIRouter(prefix="/tests", tags=["Diagnostic Tests"])


@router.get(
    "",
    response_model=PaginatedTestsResponse,
    summary="List diagnostic tests (optionally filter by centre)",
)
def list_tests(
    centre_id: str | None = Query(None, description="Filter by diagnostic centre ID"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(DiagnosticTest)
    if centre_id:
        query = query.filter(DiagnosticTest.centre_id == centre_id)
    total = query.count()
    items = query.order_by(DiagnosticTest.name).offset((page - 1) * page_size).limit(page_size).all()
    return PaginatedTestsResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[TestResponse.model_validate(t) for t in items],
    )


@router.get(
    "/{test_id}",
    response_model=TestResponse,
    summary="Get a single diagnostic test",
)
def get_test(test_id: str, db: Session = Depends(get_db)):
    test = db.query(DiagnosticTest).filter(DiagnosticTest.id == test_id).first()
    if not test:
        raise NotFoundError(f"Diagnostic test '{test_id}' not found")
    return TestResponse.model_validate(test)


@router.post(
    "",
    response_model=TestResponse,
    status_code=201,
    summary="Create a diagnostic test for a centre",
)
def create_test(payload: TestCreateRequest, db: Session = Depends(get_db)):
    # Validate that the referenced centre exists
    centre = db.query(DiagnosticCentre).filter(DiagnosticCentre.id == payload.centre_id).first()
    if not centre:
        raise NotFoundError(f"Diagnostic centre '{payload.centre_id}' not found")

    test = DiagnosticTest(
        centre_id=payload.centre_id,
        name=payload.name,
        description=payload.description,
        price=payload.price,
    )
    db.add(test)
    db.commit()
    db.refresh(test)
    return TestResponse.model_validate(test)
