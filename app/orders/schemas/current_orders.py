from decimal import Decimal

from pydantic import BaseModel, Field


class OrderResponseSchema(BaseModel):
    posting_numbe: str = Field(alias="order_posting_number")
    name: str
    expected_payout: Decimal
    price: Decimal
    quantity: int
    discount_percent_from_seller: Decimal


class OrdersDayResponseSchema(BaseModel):
    orders: list[OrderResponseSchema]
