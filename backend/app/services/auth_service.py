from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password, create_access_token
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import SignupRequest, LoginRequest, TokenResponse, UserResponse
from app.utils.exceptions import ConflictError, UnauthorizedError
from app.utils.logging import get_logger

logger = get_logger(__name__)


class AuthService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.user_repo = UserRepository(db)

    def signup(self, payload: SignupRequest) -> UserResponse:
        """Register a new user.

        Raises:
            ConflictError: If the email is already registered.
        """
        existing = self.user_repo.get_by_email(payload.email)
        if existing:
            raise ConflictError("A user with this email already exists")

        hashed = hash_password(payload.password)
        user = self.user_repo.create(
            name=payload.name,
            email=payload.email,
            hashed_password=hashed,
        )
        self.db.commit()
        self.db.refresh(user)

        logger.info("user_signed_up", user_id=user.id, email=user.email)
        return UserResponse.model_validate(user)

    def login(self, payload: LoginRequest) -> TokenResponse:
        """Authenticate a user and return a JWT.

        Raises:
            UnauthorizedError: If credentials are invalid.
        """
        user = self.user_repo.get_by_email(payload.email)
        if not user or not verify_password(payload.password, user.hashed_password):
            raise UnauthorizedError("Invalid email or password")

        token = create_access_token(subject=user.id)
        logger.info("user_logged_in", user_id=user.id)
        return TokenResponse(access_token=token)

    def get_current_user(self, user_id: str) -> User:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise UnauthorizedError("User not found")
        return user
