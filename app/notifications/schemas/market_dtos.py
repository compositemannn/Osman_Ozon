from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, model_validator

from .notification_dtos import OrderUpdatedStatusEnum


class ProductFinancialOrderDTO(BaseModel):
    commission_amount: Decimal  # Размер комиссии за товар.
    commission_percent: int  # Процент комиссии.
    payout: Decimal  # Выплата продавцу.
    price: Decimal  # Цена товара с учётом акций, кроме акций за счёт Ozon.
    old_price: Decimal
    customer_price: (
        Decimal  # Цена товара для покупателя с учётом скидок продавца и Ozon.
    )
    product_id: int
    discount_value_from_seller: Decimal | None = None
    discount_percent_from_seller: int | None = None

    @model_validator(mode="after")
    def calculate_discounts(self):
        self.discount_value_from_seller = self.old_price - self.price

        if self.old_price == 0:
            self.discount_percent_from_seller = 0
        else:
            self.discount_percent_from_seller = int(
                (self.discount_value_from_seller / self.old_price) * 100
            )

        return self


class FinancialOrderDataDTO(BaseModel):
    products: list[ProductFinancialOrderDTO]


class ProductOrderDTO(BaseModel):
    name: str
    quantity: int
    sku: int
    offer_id: str


class ReceivedOrderDTO(BaseModel):
    posting_number: str
    status: OrderUpdatedStatusEnum
    in_process_at: datetime  # Дата и время начала обработки отправления.
    shipment_date: datetime
    products: list[ProductOrderDTO]
    financial_data: FinancialOrderDataDTO


class ReceivedBusinessOrderDTO(BaseModel):
    result: ReceivedOrderDTO
