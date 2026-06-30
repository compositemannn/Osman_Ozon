from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class OrderResponseSchema(BaseModel):
    posting_number: str = Field(alias="order_posting_number")
    name: str
    expected_payout: Decimal
    price: Decimal
    quantity: int
    discount_percent_from_seller: Decimal

    model_config = ConfigDict(from_attributes=True)


class OrdersDayResponseSchema(BaseModel):
    items: list[OrderResponseSchema]

    model_config = ConfigDict(from_attributes=True)
