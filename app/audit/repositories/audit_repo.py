from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.models.audit import AuditDay
from app.infrastructure.models.audit_actions import AuditAction
from datetime import date
from sqlalchemy.orm import selectinload
from sqlalchemy import (
    func,
    select,
)


class AuditRepository:
    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

    async def get_or_create_day(self, target_date: date):
        stmt = (
            select(AuditDay)
            .where(AuditDay.date == target_date)
            .options(selectinload(AuditDay.actions))
        )
        result = await self.session.execute(stmt)
        table = result.scalar_one_or_none()
        if table is None:
            table = AuditDay(date=target_date, initial_cash=0)
            self.session.add(table)
            await self.session.commit()
            await self.session.refresh(table)
        return table

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