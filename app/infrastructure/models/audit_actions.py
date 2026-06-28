from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class AuditAction(Base):
    __tablename__ = "audit_actions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    audit_day_id: Mapped[int] = mapped_column(
        ForeignKey("audit_days.id"),
        nullable=False,
    )

    audit_day: Mapped["AuditDay"] = relationship(  # noqa: F821  # pyright: ignore[reportUndefinedVariable]
        back_populates="actions"
    )

    actor: Mapped[str] = mapped_column(String)
    action: Mapped[str] = mapped_column(String)
    money: Mapped[int] = mapped_column(Integer)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
