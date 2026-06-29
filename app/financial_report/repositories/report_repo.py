from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.models.order import Order
from app.infrastructure.models.order_item import OrderItem
from datetime import date, datetime, time, timezone
from sqlalchemy import select, or_, and_
from sqlalchemy.orm import selectinload
from decimal import Decimal

class ReportRepository:
    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

    async def get_financial_orders(self, target_date: date):
        # Настраиваем временные границы суток в UTC
        start_dt = datetime.combine(target_date, time.min, tzinfo=timezone.utc)
        end_dt = datetime.combine(target_date, time.max, tzinfo=timezone.utc)

        # Собираем запрос с условием ИЛИ
        query = (
            select(Order)
            .where(
                or_(
                    # Условие 1: Доставлен сегодня
                    and_(
                        Order.status == "delivered",
                        Order.last_event_time >= start_dt,
                        Order.last_event_time <= end_dt
                    ),
                    # Условие 2: Оплачен Озоном сегодня
                    Order.payout_date == target_date
                )
            )
            .options(
                selectinload(Order.items)  # Жадная загрузка товаров (избегаем N+1)
            )
        )
        
        result = await self.session.execute(query)
        # Возвращаем список уникальных объектов Order
        return list(result.scalars().all())
    
    async def update_order_payout(self, posting_number: str, payout_amount: Decimal, payout_date: date):
        stmt = select(Order).where(Order.posting_number == posting_number)
        result = await self.session.execute(stmt)
        order = result.scalars().first()
        
        # Добавляем проверку на существование заказа
        if order:
            order.payout = payout_amount
            # Приводим date к datetime с таймзоной UTC, чтобы соответствовать модели
            order.payout_date = datetime.combine(payout_date, time.min, tzinfo=timezone.utc)
            
            await self.session.commit()