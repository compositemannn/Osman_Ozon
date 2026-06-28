from datetime import date
from typing import Any

from fastapi import HTTPException, status

from app.audit.repositories.audit_repo import AuditRepository
from app.audit.schemas.AuditDayDTO import AuditDayFullResponse
from app.infrastructure.models.audit import AuditDay


class AuditHandler:
    def __init__(self, repo: AuditRepository, payload: dict[str, Any] = None):
        self.repo = repo
        self.payload = payload

    async def get_or_create_day(self, target_date: date):
        audit_from_db = await self.repo.get_day(target_date)
        if audit_from_db is None:
            if target_date == date.today():
                audit_from_db = await self.repo.create_day(target_date)

            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Такого дня не существует.",
                )

        await self.repo.session.commit()

        valid_audit_day = AuditDayFullResponse.model_validate(audit_from_db)

        return valid_audit_day

    async def create_action(self):
        if self.payload is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Тело запроса (payload) не может быть пустым",
            )
        action = await self.repo.create_action(self.payload)
        return action

    async def update_action(self, id):
        if self.payload is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Тело запроса (payload) не может быть пустым",
            )
        action = await self.repo.update_action(id, self.payload)
        if action is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Запись для обновления не найдена",
            )
        return action

    async def delete_action(self, id):
        flag = await self.repo.delete_action(id)
        if flag is False:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Запись для удаления не найдена",
            )
        return {"status": "success", "message": "Запись успешно удалена"}
