from datetime import timezone
from decimal import Decimal

from app.infrastructure.models.order import Order
from app.infrastructure.models.order_item import OrderItem

from .market_dtos import (
    ProductFinancialOrderDTO,
    ProductOrderDTO,
    ReceivedOrderDTO,
)


class OrderValidation:
    @staticmethod
    async def convert_item_to_model(
        item_dto: ProductOrderDTO, financial_data_dto: ProductFinancialOrderDTO
    ):
        order_item = OrderItem(
            name=item_dto.name,
            sku=item_dto.sku,
            quantity=item_dto.quantity,
            price=financial_data_dto.price,
            commission_amount=financial_data_dto.commission_amount,
            expected_payout=financial_data_dto.payout,
            commission_percent=financial_data_dto.commission_percent,
            customer_price=financial_data_dto.customer_price,
            old_price=financial_data_dto.old_price,
            discount_value_from_seller=financial_data_dto.discount_value_from_seller,
            discount_percent_from_seller=financial_data_dto.discount_percent_from_seller,
        )
        return order_item

    @staticmethod
    def convert_order_to_model(order_dto: ReceivedOrderDTO, expected_payout: Decimal):
        order = Order(
            posting_number=order_dto.posting_number,
            status="заказ создан",
            last_event_time=order_dto.in_process_at.astimezone(timezone.utc),
            expected_payout=expected_payout,
        )
        return order
