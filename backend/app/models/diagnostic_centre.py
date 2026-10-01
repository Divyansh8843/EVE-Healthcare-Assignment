import uuid

from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from app.core.database import Base


class DiagnosticCentre(Base):
    __tablename__ = "diagnostic_centres"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[str] = mapped_column(String(500), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    tests: Mapped[list["DiagnosticTest"]] = relationship(  # noqa: F821
        "DiagnosticTest", back_populates="centre", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<DiagnosticCentre id={self.id} name={self.name}>"
