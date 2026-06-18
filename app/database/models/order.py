from datetime import datetime, timezone
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.db import Base


class Order(Base):
    __tablename__ = "orders"

    posting_number: Mapped[str] = mapped_column(
        String(50),
        primary_key=True
    )

    status: Mapped[str] = mapped_column(
        String(50),
        index=True # по статусам часто выборки делать будем
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    # Дата изменения статуса. При создании ставим текущее время UTC, 
    # а при любом изменении строки (onupdate) база сама обновит время на актуальное.
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    items: Mapped[list["OrderItem"]] = relationship(back_populates="order")