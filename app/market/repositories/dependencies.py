from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.repositories.order_repo import OrderRepository


async def get_repo_obj(session: AsyncSession = Depends(get_db)):
    repo = OrderRepository(session)

    return repo
