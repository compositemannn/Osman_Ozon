from infrastructure.models.order import Order
from infrastructure.models.order_item import OrderItem
from infrastructure.models.stock_item import StockItem
from sqlalchemy import (
    func,
    select,
)
from sqlalchemy.ext.asyncio import AsyncSession


class NotificationsRepository:
    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

    async def get_order_item_total_quantity(
        self, posting_number: str, sku: int
    ) -> int | None:
        stmt = select(func.sum(OrderItem.quantity)).where(
            OrderItem.order_posting_number == posting_number, OrderItem.sku == sku
        )

        result = await self.session.execute(stmt)

        quantity: int | None = result.scalar_one_or_none()

        return quantity

    async def get_order_by_posting_number_or_none(
        self, posting_number: str
    ) -> Order | None:
        stmt = select(Order).where(Order.posting_number == posting_number)

        result = await self.session.execute(stmt)
        existing_order = result.scalar_one_or_none()

        return existing_order

    async def get_order_item_by_sku(
        self, posting_number: str, sku: int
    ) -> OrderItem | None:
        stmt = select(OrderItem).where(
            OrderItem.order_posting_number == posting_number, OrderItem.sku == sku
        )

        result = await self.session.execute(stmt)

        existing_item: OrderItem | None = result.scalar_one_or_none()

        return existing_item

    async def create_order_with_items(
        self, order: Order, order_items: list[OrderItem]
    ) -> Order:
        order.items = order_items

        self.session.add(order)
        await self.session.flush()

        return order

    async def get_stock_batch_by_sku_purchase_price(self, sku: int, purchase_price):
        stmt = (
            select(StockItem.quantity)
            .where(StockItem.sku == sku)
            .order_by(StockItem.purchase_price)
            .limit(1)
        )

        result = await self.session.execute(stmt)
        batches = result.scalars().all()

        return batches

    async def get_stock_batch_by_sku(self, sku: int):
        stmt = (
            select(StockItem)
            .where(StockItem.sku == sku, StockItem.current_quantity > 0)
            .order_by(StockItem.created_at)
        )
        result = await self.session.execute(stmt)
        batches = result.scalars().all()

        return batches
