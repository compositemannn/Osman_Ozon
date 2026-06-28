from datetime import date

from sqlalchemy import (
    func,
    select,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.infrastructure.models.audit import AuditDay
from app.infrastructure.models.audit_actions import AuditAction


class AuditRepository:
    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

    async def get_day(self, target_date: date):
        stmt = (
            select(AuditDay)
            .where(AuditDay.creation_date == target_date)
            .options(selectinload(AuditDay.actions))
        )
        result = await self.session.execute(stmt)
        audit = result.scalar_one_or_none()

        return audit

    async def create_day(self, current_date: date):
        audit_day = AuditDay(creation_date=current_date, is_editable=True)
        self.session.add(audit_day)

        await self.session.flush()

        return audit_day

    async def create_action(self, action_data: dict):
        model_orm = AuditAction(**action_data)
        self.session.add(model_orm)
        await self.session.commit()
        await self.session.refresh(model_orm)
        return model_orm

    async def update_action(self, action_id: int, update_data: dict):
        stmt = select(AuditAction).where(AuditAction.id == action_id)
        result = await self.session.execute(stmt)
        action = result.scalar_one_or_none()

        if action is None:
            return None

        for key, value in update_data.items():
            setattr(action, key, value)

        await self.session.commit()
        await self.session.refresh(action)

        return action

    async def delete_action(self, id):
        stmt = select(AuditAction).where(AuditAction.id == id)
        result = await self.session.execute(stmt)
        action = result.scalar_one_or_none()

        if action:
            await self.session.delete(action)
            await self.session.commit()
            return True

        return False
