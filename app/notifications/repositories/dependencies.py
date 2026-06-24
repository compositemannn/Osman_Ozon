from fastapi import Depends
from infrastructure.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

from .order_repo import OrderRepository


async def get_repo_obj(session: AsyncSession = Depends(get_db)):
    repo = OrderRepository(session)

    return repo
