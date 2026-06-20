from typing import Any

from app.clients.request_to_market import get_order
from app.repositories.models.order import Order
from app.repositories.order_repo import OrderRepository
from app.schemas.notification import NotificationTypeEnum, OrderCreatedNotificationDTO
from app.schemas.order_from_market import ReceivedBusinessOrderDTO, ReceivedOrderDTO
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


    async def _get_parsed_order_from_market(self, posting_number: str):
        raw_order_from_market = get_order(posting_number)
        order_from_market = ReceivedBusinessOrderDTO.model_validate(raw_order_from_market)
        order_data: ReceivedOrderDTO = order_from_market.result

        return order_data

    async def _handle_order_created(self):
        order_created_notification = OrderCreatedNotificationDTO.model_validate(self.payload)

        existing_order = self.repo.get_order_by_posting_number_or_none(order_created_notification.posting_number)

        if existing_order:
            return

        order_data: ReceivedOrderDTO = self._get_parsed_order_from_market(order_created_notification.posting_number)

        order_model = OrderValidation.convert_order_to_model(order_data)

        for item, item_financial_data in zip(order_data.products, order_data.financial_data.products):
            qty_to_deduct = item.quantity
            batches = self.repo.get_stock_batch_by_sku(item.sku)

            for batch in batches:
                allocated_qty = min(batch.current_quantity, qty_to_deduct)
                batch.current_quantity -= allocated_qty
                qty_to_deduct -= allocated_qty

                order_item_model = OrderValidation.convert_item_to_model(
                    item, item_financial_data, allocated_qty, batch.purchase_price
                )
                self.repo.create_order_with_items(order_model, order_item_model)

        self.repo.session.commit()
