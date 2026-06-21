from sqlalchemy import String, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Product(Base):
    __tablename__ = "products"

    sku: Mapped[int] = mapped_column(
        BigInteger,
        primary_key = True
    )

    offer_id: Mapped[str] = mapped_column(
        String(100),
        index = True
    )

    name: Mapped[str] = mapped_column(
        String(255)
    )

    batches: Mapped[list["StockBatch"]] = relationship(back_populates="product")
