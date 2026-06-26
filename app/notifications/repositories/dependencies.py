from fastapi import Depends
from infrastructure.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

from .notifications import NotificationsRepository


async def get_repo_obj(session: AsyncSession = Depends(get_db)):
    repo = NotificationsRepository(session)

    return repo
