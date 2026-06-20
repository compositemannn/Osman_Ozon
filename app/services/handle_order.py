from typing import Any

from app.repositories.models.order import Order
from app.repositories.order_repo import OrderRepository
from app.schemas.notification import NotificationTypeEnum, OrderCreatedNotificationDTO
from app.schemas.order_validation import OrderValidation


class NotificationHandler:
    def __init__(self,
                notification_type: NotificationTypeEnum,
                payload: dict[str, Any],
                repo: OrderRepository
                ):

        self.notification_type: NotificationTypeEnum = notification_type
        self.repo: OrderRepository = repo
        self.payload: dict[str, Any] = payload

    async def notification_distribution(self):
        handlers = {
            NotificationTypeEnum.TYPE_NEW_POSTING: self._handle_order_created,
        }

        handler = handlers.get(self.notification_type)

        if handler is None:
            raise ValueError(
                "Unsupported notification type: " +
                f"{self.notification_type}"
            )

        return await handler()


    async def _get_parsed_order_from_market(self):
        ...


    async def __handle_order_created(self):
        order_created_notification: OrderCreatedNotificationDTO = OrderValidation.validate_raw_notification_order_created(self.payload)

        existing_order = self.repo.get_order_by_posting_number_or_none(order_created_notification.posting_number)
        if existing_order:
            return
