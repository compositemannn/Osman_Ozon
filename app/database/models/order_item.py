from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy import BigInteger, Integer, Numeric, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.db import Base


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key = True
    )

    posting_number: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("orders.posting_number"),
        index = True
    )

    sku: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("products.sku"),
        index = True
    )

    quantity: Mapped[int] = mapped_column(
        Integer
    )

    # Количество отмененного товара в этой позиции (по умолчанию 0)
    quantity_cancelled: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )

    price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2)
    )

    # Сумма комиссии, которую Ozon забирает себе за продажу
    commission_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )

    # Чистая выплата на наш счет за товар (price - commission_amount)
    payout: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )

    purchase_price: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2),
        nullable = True
    )

    order: Mapped["Order"] = relationship(back_populates = "items")

    product: Mapped["Product"] = relationship()