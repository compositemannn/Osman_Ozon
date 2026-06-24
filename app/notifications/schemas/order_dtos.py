from datetime import datetime
from decimal import Decimal

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class OrderDTO(BaseModel):
    """CreateOrderDTO"""

    model_config = ConfigDict(
        use_enum_values=True, populate_by_name=True, from_attributes=True
    )

    posting_number: str | None = None
    status: str | None = None
    last_event_time: datetime | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "in_process_at",
            "changed_state_date",
        ),
    )


class OrderItemsStockBatchProductBase(BaseModel):
    model_config = ConfigDict(
        use_enum_values=True, populate_by_name=True, from_attributes=True
    )

    sku: int


class OrderItemDTO(OrderItemsStockBatchProductBase):
    """CreateOrderItemDTO"""

    quantity: int | None = None
    commission_amount: Decimal | None = None  # Размер комиссии за товар.
    commission_percent: int | None = None  # Процент комиссии.
    payout: Decimal  # Выплата продавцу.
    price: Decimal  # Цена товара с учётом акций, кроме акций за счёт Ozon.
    customer_price: (
        Decimal  # Цена товара для покупателя с учётом скидок продавца и Ozon.
    )
    total_discount_percent: Decimal  # Процент скидки.
    total_discount_value: Decimal  # Сумма скидки.
    purchase_price: Decimal


class StockBatchDTO(OrderItemsStockBatchProductBase):
    purchase_price: Decimal
    curren_quantity: int
    initial_quantity: int


class ProductDTO(OrderItemsStockBatchProductBase):
    offer_id: int
    name: str
