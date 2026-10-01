from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.utils.exceptions import UnauthorizedError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """FastAPI dependency: validates JWT and returns the current User.

    Raises:
        UnauthorizedError: if the token is missing, expired, or invalid.
    """
    user_id = decode_access_token(token)
    if not user_id:
        raise UnauthorizedError("Invalid or expired token")

    user = UserRepository(db).get_by_id(user_id)
    if not user:
        raise UnauthorizedError("User account not found")

    return user
