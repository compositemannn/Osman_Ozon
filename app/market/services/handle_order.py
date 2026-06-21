from typing import Any

from app.clients.request_to_market import get_order
from app.repositories.order_repo import OrderRepository
from app.schemas.notification_dtos import NotificationTypeEnum, OrderCreatedNotificationDTO, OrderUpdatedStatusNotificationDTO
from app.schemas.market_dtos import ReceivedBusinessOrderDTO, ReceivedOrderDTO
from app.schemas.transform import OrderValidation
from app.schemas.response_dtos import HandlerResponse


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
            NotificationTypeEnum.TYPE_STATE_CHANGED: self._handle_order_status_updated,
            HandlerException.ORDER_IS_NOT_EXIST_IN_DB: self._handle_order_created
        }

        handler = handlers.get(self.notification_type)

        if handler is None:
            raise ValueError(
                "Unsupported notification type: " +
                f"{self.notification_type}"
            )

        return await handler()


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

        return HandlerResponse.OK


    async def _handle_order_status_updated(self):
        order_updated_status_notification = OrderUpdatedStatusNotificationDTO.model_validate(self.payload)

        existing_order = self.repo.get_order_by_posting_number_or_none(order_updated_status_notification.posting_number)

        if existing_order is None:
            return self.notification_distribution(HandlerResponse.ORDER_IS_NOT_EXIST_IN_DB)

        last_event_time_from_db = existing_order.last_event_time
        last_event_time_from_notification = order_updated_status_notification.changed_state_date

        if last_event_time_from_notification < last_event_time_from_db:
            return

        existing_order.status = order_updated_status_notification.new_state

        await self.repo.session.commit()

        return HandlerResponse.OK



    @staticmethod
    async def _get_parsed_order_from_market(posting_number: str):
        raw_order_from_market = get_order(posting_number)
        order_from_market = ReceivedBusinessOrderDTO.model_validate(raw_order_from_market)
        order_data: ReceivedOrderDTO = order_from_market.result

        return order_data
