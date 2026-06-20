from typing import Any
from app.schemas.notification import OrderCreatedNotificationDTO, OrderUpdatedStatusNotificationDTO


class OrderValidation:
    @staticmethod
    def parse_raw_notification_order_created(raw_notification: dict[str, Any]):
        return OrderCreatedNotificationDTO.model_validate(raw_notification)

    @staticmethod
    def parse_raw_notification_order_status_updated(raw_notification: dict[str, Any]):
        return OrderUpdatedStatusNotificationDTO.model_validate(raw_notification)

    @staticmethod
    def parse_order_from_market(posting_number: str):
        return
