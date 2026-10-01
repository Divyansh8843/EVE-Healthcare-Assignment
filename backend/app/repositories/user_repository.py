from typing import Optional

from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    """Data-access layer for User objects."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email.lower()).first()

    def get_by_id(self, user_id: str) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def create(self, name: str, email: str, hashed_password: str) -> User:
        user = User(name=name, email=email.lower(), hashed_password=hashed_password)
        self.db.add(user)
        self.db.flush()   # assigns id without committing — caller owns the transaction
        return user
