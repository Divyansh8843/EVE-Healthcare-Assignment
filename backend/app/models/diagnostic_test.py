import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import String, DateTime, Numeric, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class DiagnosticTest(Base):
    __tablename__ = "diagnostic_tests"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    centre_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("diagnostic_centres.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
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
    centre: Mapped["DiagnosticCentre"] = relationship(  # noqa: F821
        "DiagnosticCentre", back_populates="tests"
    )

    def __repr__(self) -> str:
        return f"<DiagnosticTest id={self.id} name={self.name} price={self.price}>"
