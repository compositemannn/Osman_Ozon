from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy import BigInteger, Integer, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.db import Base


class StockBatch(Base):
    __tablename__ = "stock_batches"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key = True
    )

    sku: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("products.sku"),
        index = True
    )

    purchase_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2)
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    current_quantity: Mapped[int] = mapped_column(
        Integer
    )

    initial_quantity: Mapped[int] = mapped_column(
        Integer
    )

    product: Mapped["Product"] = relationship(back_populates="batches")

