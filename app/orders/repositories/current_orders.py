from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.models.order import Order


class CurrentOrdersRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_orders_by_day(self, day: date):
        stmt = select(Order.items).where(Order.created_at.date == day)

        result = await self.session.execute(stmt)
        orders_items = result.scalars().all()

        return orders_items
