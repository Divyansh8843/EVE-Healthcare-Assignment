from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.auth import SignupRequest, LoginRequest, TokenResponse, UserResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/signup",
    response_model=UserResponse,
    status_code=201,
    summary="Register a new user",
    description="Create a new user account. Returns the user profile (no token).",
)
def signup(payload: SignupRequest, db: Session = Depends(get_db)):
    return AuthService(db).signup(payload)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Log in and receive a JWT",
    description="Authenticate with email and password. Returns a Bearer access token.",
)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    return AuthService(db).login(payload)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current authenticated user",
)
def me(current_user: User = Depends(get_current_user)):
    return current_user
