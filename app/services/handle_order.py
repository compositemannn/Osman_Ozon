from typing import Any

from app.repositories.order_repo import OrderRepository
from app.schemas.notification import NotificationTypeEnum, OrderCreatedNotificationDTO


class NotificationHandler:
    def __init__(self,
                notification_type: NotificationTypeEnum,
                payload: dict[str, Any],
                repo: OrderRepository
                ):

        self.notification_type: NotificationTypeEnum = notification_type
        self.repo: OrderRepository = repo

    async def handle(self):
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

    async def _handle_order_created(self):
        pass
