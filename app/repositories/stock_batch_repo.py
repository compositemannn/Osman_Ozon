from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.models.stock_batch import StockBatch
from sqlalchemy import update, select, asc # asc - по возрастанию (первые - самые старые партии)
from datetime import timezone


class StockBatchRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_product_from_stock_butch_or_none(self, sku: int) -> list[StockBatch]:
        stmt = select(StockBatch
                ).where(StockBatch.sku == sku, StockBatch.current_quantity > 0
                ).order_by(asc(StockBatch.created_at)
            )

        result = await self.session.execute(stmt)
        batch = result.scalars().all()

        return batch
