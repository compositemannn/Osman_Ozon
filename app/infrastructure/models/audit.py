from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import DateTime, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class AuditDay(Base):
    __tablename__ = "audit_days"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    initial_cash: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, default=0
    )

    actions: Mapped[list["AuditAction"]] = relationship(  # noqa: F821  # pyright: ignore[reportUndefinedVariable]
        back_populates="audit_day",
        cascade="all, delete-orphan",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
