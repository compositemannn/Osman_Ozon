from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy import Boolean, Date, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class AuditDay(Base):
    __tablename__ = "audit_days"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    initial_cash: Mapped[Decimal] = mapped_column(Integer, default=0)

    actions: Mapped[list["AuditAction"]] = relationship(  # noqa: F821  # pyright: ignore[reportUndefinedVariable]
        back_populates="audit_day",
        cascade="all, delete-orphan",
    )

    creation_date: Mapped[date] = mapped_column(Date, nullable=False)

    final_cash: Mapped[Decimal] = mapped_column(Integer, default=0)

    is_editable: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
