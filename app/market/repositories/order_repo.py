from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.models.order import Order
from app.repositories.models.order_item import OrderItem
from sqlalchemy import select, asc, func # asc - по возрастанию (первые - самые старые партии)

from app.repositories.models.stock_batch import StockBatch


class OrderRepository:
    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

    async def get_order_item_total_quantit(self, posting_number: str, sku: int):
        stmt = select(func.sum(OrderItem.quantity)
                ).where(OrderItem.posting_number == posting_number,
                        OrderItem.sku == sku
                )

        result = await self.session.execute(stmt)

        existing_item = result.scalar_one_or_none()

        return existing_item


    async def get_order_by_posting_number_or_none(self, posting_number: str) -> Order | None:
        stmt = select(Order).where(Order.posting_number == posting_number)
        result = await self.session.execute(stmt)

        existing_order = result.scalar_one_or_none()

        return existing_order


    async def get_order_item_by_sku(self, posting_number: str, sku: int):
        stmt = select(OrderItem
                ).where(OrderItem.posting_number == posting_number,
                        OrderItem.sku == sku,
                        OrderItem.quantity > 0
                ).order_by(OrderItem.purchase_price
                ).limit(1)

        result = await self.session.execute(stmt)

        existing_item = result.scalar_one_or_none()

        return existing_item


    async def create_order_with_items(self,
        order: Order,
        order_items: list[OrderItem]
    ) -> Order:
        order.items = order_items

        self.session.add(order)
        await self.session.flush()

        return order

    async def get_stock_batch_by_sku_purchase_price(self, sku: int, purchase_price):
        stmt = select(StockBatch.quantity
                ).where(StockBatch.sku == sku
                ).order_by(StockBatch.purchase_price
                ).limit(1)

        result = await self.session.execute(stmt)
        batches = result.scalars().all()

        return batches

    async def get_stock_batch_by_sku(self, sku: int):
        stmt = select(StockBatch
                ).where(StockBatch.sku == sku, StockBatch.current_quantity > 0
                ).order_by(asc(StockBatch.created_at)
                )
        result = await self.session.execute(stmt)
        batches = result.scalars().first()

        return batches
