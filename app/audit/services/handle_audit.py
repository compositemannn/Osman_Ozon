from app.audit.repositories.audit_repo import AuditRepository
from typing import Any
from datetime import date
from app.infrastructure.models.audit import AuditDay
from fastapi import HTTPException, status

class AuditHandler:
    def __init__(self, repo: AuditRepository, payload: dict[str, Any] = None):
        self.repo = repo
        self.payload = payload
    
    async def get_or_create_day(self, target_date: date):
        if target_date > date.today():
            # Для будущего дня касса пустая, редактировать нельзя
            day = AuditDay(date=target_date, initial_cash=0, actions=[])
            day.final_cash = 0
            day.is_editable = False
            return day
        day = await self.repo.get_or_create_day(target_date)
        total_cash = day.initial_cash
        for action in day.actions:
            # money в схемах — это int (может быть с плюсом или минусом)
            total_cash += action.money

        day.final_cash = total_cash
        day.is_editable = True  # Разрешаем редактировать текущий/прошлые дни
        return day
    
    async def create_action(self):
        if self.payload is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Тело запроса (payload) не может быть пустым"
            )
        action = await self.repo.create_action(self.payload)
        return action

    async def update_action(self, id):
        if self.payload is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Тело запроса (payload) не может быть пустым"
            )
        action = await self.repo.update_action(id, self.payload)
        if action is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Запись для обновления не найдена"
            )
        return action

    async def delete_action(self, id):
        flag = await self.repo.delete_action(id)
        if flag is False:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Запись для удаления не найдена"
            )
        return {"status": "success", "message": "Запись успешно удалена"}