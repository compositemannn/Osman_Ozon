from typing import Any

from infrastructure.models.order_item import OrderItem

from ..clients.request_to_market import get_order
from ..repositories.order_repo import OrderRepository
from ..schemas.market_dtos import ReceivedBusinessOrderDTO, ReceivedOrderDTO
from ..schemas.notification_dtos import (
    STATUS_LABELS,
    NotificationTypeEnum,
    OrderCancelledNotificationDTO,
    OrderCreatedNotificationDTO,
    OrderUpdatedStatusNotificationDTO,
)
from ..schemas.response_dtos import HandlerResponse
from ..schemas.transform import OrderValidation


class NotificationHandler:
    def __init__(self, payload: dict[str, Any], repo: OrderRepository):
        self.repo: OrderRepository = repo
        self.payload: dict[str, Any] = payload

    async def notification_distribution(self, notification_type):
        handlers = {
            NotificationTypeEnum.TYPE_NEW_POSTING: (
                self._handle_order_created,
                OrderCreatedNotificationDTO.model_validate(notification_type),
            ),
            NotificationTypeEnum.TYPE_STATE_CHANGED: (
                self._handle_order_status_updated,
                OrderUpdatedStatusNotificationDTO.model_validate(notification_type),
            ),
            HandlerResponse.ORDER_IS_NOT_EXIST_IN_DB: (
                self._handle_order_created,
                OrderCreatedNotificationDTO.model_validate(notification_type),
            ),
        }

        handler = handlers.get(notification_type)

        if handler is None:
            raise ValueError("Unsupported notification type: " + f"{notification_type}")

        return await handler()

    async def _handle_order_created(self, notification: OrderCreatedNotificationDTO):
        existing_order = await self.repo.get_order_by_posting_number_or_none(
            notification.posting_number
        )

        if existing_order:
            return

        order_data: ReceivedOrderDTO = await self._get_parsed_order_from_market(
            notification.posting_number
        )

        if order_data is not None:
            order_model = OrderValidation.convert_order_to_model(order_data)
            order_item_models: list[OrderItem] = []

            for item, item_financial_data in zip(
                order_data.products, order_data.financial_data.products
            ):
                qty_to_deduct = item.quantity
                batches = await self.repo.get_stock_batch_by_sku(item.sku)

                for batch in batches:
                    allocated_qty = min(batch.current_quantity, qty_to_deduct)
                    batch.current_quantity -= allocated_qty
                    qty_to_deduct -= allocated_qty

                    order_item_model = await OrderValidation.convert_item_to_model(
                        item, item_financial_data, allocated_qty, batch.purchase_price
                    )
                    order_item_models.append(order_item_model)

            await self.repo.create_order_with_items(order_model, order_item_models)

            await self.repo.session.commit()

        return HandlerResponse.OK

    async def _handle_order_status_updated(
        self, notification: OrderUpdatedStatusNotificationDTO
    ):
        existing_order = await self.repo.get_order_by_posting_number_or_none(
            notification.posting_number
        )

        if existing_order is None:
            return self.notification_distribution(
                HandlerResponse.ORDER_IS_NOT_EXIST_IN_DB
            )

        last_event_time_from_db = existing_order.last_event_time
        last_event_time_from_notification = notification.changed_state_date

        if last_event_time_from_notification < last_event_time_from_db:
            return

        existing_order.status = STATUS_LABELS[notification.new_state]

        await self.repo.session.commit()

        return HandlerResponse.OK

    async def _handle_order_item_cancelled(
        self, notification: OrderCancelledNotificationDTO
    ):
        existing_order = await self.repo.get_order_by_posting_number_or_none(
            notification.posting_number
        )

        if existing_order is None:
            return self.notification_distribution(
                HandlerResponse.ORDER_IS_NOT_EXIST_IN_DB
            )

        for item in notification.products:
            qty_to_detuct = item.quantity

            total_qty = await self.repo.get_order_item_total_quantity(
                notification.posting_number, item.sku
            )

            item_from_db: OrderItem | None = await self.repo.get_order_item_by_sku(
                notification.posting_number, item.sku
            )

            if total_qty is not None:
                # qty_from_stock_batch = (
                #     await self.repo.get_stock_batch_by_sku_purchase_price(
                #         item.sku, item_from_db.purchase_price
                #     )
                # )

                while (
                    item_from_db is not None and qty_to_detuct > item_from_db.quantity
                ):
                    qty_to_detuct -= item_from_db.quantity
                    item_from_db.quantity = 0

                    item_from_db = await self.repo.get_order_item_by_sku(
                        notification.posting_number,
                        item.sku,
                    )

                if item_from_db is None:
                    continue

                item_from_db.quantity -= qty_to_detuct

        await self.repo.session.commit()

        return HandlerResponse.OK

    @staticmethod
    async def _get_parsed_order_from_market(posting_number: str):
        raw_order_from_market = await get_order(posting_number)
        order_from_market = ReceivedBusinessOrderDTO.model_validate(
            raw_order_from_market
        )
        order_data: ReceivedOrderDTO = order_from_market.result

        return order_data
