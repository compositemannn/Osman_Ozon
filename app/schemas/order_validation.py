from typing import Any
from app.schemas.notification import OrderCreatedNotificationDTO, OrderUpdatedStatusNotificationDTO


class OrderValidation:
    def __init__(self, raw_notification_data: dict[str, Any]):
        self.__raw_notification: dict[str, Any] = raw_notification_data

    @property
    def validate_raw_notification_order_created(self):
        return OrderCreatedNotificationDTO.model_validate(self.__raw_notification)

    @property
    def validate_raw_notification_order_status_updated(self):
        return OrderUpdatedStatusNotificationDTO.model_validate(self.__raw_notification)
