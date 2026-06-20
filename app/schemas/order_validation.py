from statistics import quantiles
from typing import Any
from app.repositories.models.order import Order
from app.repositories.models.order_item import OrderItem
from app.schemas.notification import OrderCreatedNotificationDTO, OrderUpdatedStatusNotificationDTO
from app.schemas.order_from_market import FinancialOrderDataDTO, ProductFinancialOrderDTO, ProductOrderDTO, ReceivedBusinessOrderDTO, ReceivedOrderDTO


class OrderValidation:
    @staticmethod
    async def convert_item_to_model(item_dto: ProductOrderDTO,  financial_data_dto: ProductFinancialOrderDTO, allocated_qty: int, purchase_price):
        order_item = OrderItem(
            sku=item_dto.sku,
            quantity=allocated_qty,
            price=financial_data_dto.price,
            commission_amount=financial_data_dto.commission_amount,
            payout=financial_data_dto.payout,
            purchase_price=purchase_price,
            commission_percent=financial_data_dto.commission_percent,
            customer_price=financial_data_dto.customer_price,
            total_discount_percent=financial_data_dto.total_discount_percent,
            total_discount_value=financial_data_dto.total_discount_value,
        )
        return order_item

    @staticmethod
    def convert_order_to_model(order_dto: ReceivedOrderDTO):
        order = Order(
            posting_number=order_dto.posting_number,
            status=order_dto.status,
            last_event_time=order_dto.in_process_at
        )
        return order

    # @staticmethod
    # def parse_raw_notification_order_created(raw_notification: dict[str, Any]):
    #     return OrderCreatedNotificationDTO.model_validate(raw_notification)

    # @staticmethod
    # def parse_raw_notification_order_status_updated(raw_notification: dict[str, Any]):
    #     return OrderUpdatedStatusNotificationDTO.model_validate(raw_notification)

    # @staticmethod
    # def parse_order_from_market(raw_information_about_order: str):
    #     return ReceivedBusinessOrderDTO.model_validate(raw_information_about_order)
