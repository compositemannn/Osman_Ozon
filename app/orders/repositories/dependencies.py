from fastapi import Depends
from infrastructure.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

from .current_orders import CurrentOrdersRepository


async def get_repo_current_orders_obj(session: AsyncSession = Depends(get_db)):
    repo = CurrentOrdersRepository(session)

    return repo
