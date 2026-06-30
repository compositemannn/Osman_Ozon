from fastapi import Depends
from app.infrastructure.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

from app.financial_report.repositories.report_repo import ReportRepository


async def get_repo_obj(session: AsyncSession = Depends(get_db)):
    repo = ReportRepository(session)

    return repo