import asyncio

from .database import Base, engine

# импортируешь ВСЕ модели
from .models.audit import AuditDay
from .models.audit_actions import AuditAction
from .models.order import Order
from .models.order_item import OrderItem
from .models.stock_item import StockItem


async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    asyncio.run(create_db())
