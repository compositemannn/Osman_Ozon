from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.models.order import Order
from app.repositories.models.order_item import OrderItem
from sqlalchemy import update, select, asc # asc - по возрастанию (первые - самые старые партии)
from datetime import timezone


class OrderRepository:
    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session


    async def get_order_by_posting_number_or_none(self, posting_number: str) -> Order | None:
        stmt = select(Order).where(Order.posting_number == posting_number)
        result = await self.session.execute(stmt)

        existing_order = result.scalar_one_or_none()

        return existing_order


    async def create_order_with_items(self,
        order: Order,
        order_items: list[OrderItem]
    ) -> Order:
        order.items = order_items

        self.session.add(order)
        await self.session.flush()

        return order
