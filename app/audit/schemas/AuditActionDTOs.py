from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

class AuditActionCreate(BaseModel):
    """Схема для создания новой строки (POST /api/audit/action).
    Присылается фронтендом, когда сотрудник добавляет действие.
    """
    actor: str = Field(..., description="Кто совершил действие")
    action: str = Field(..., description="Само действие с кассой")
    money: int = Field(..., description="Количество денег (приход/расход)")
    audit_day_id: int = Field(..., description="ID кассового дня, к которому привязана строка")

class AuditActionUpdate(BaseModel):
    """Схема для точечного изменения строки (PATCH /api/audit/action/{id}).
    Все поля необязательные, фронтенд может прислать только то, что изменилось.
    """
    actor: Optional[str] = Field(None, description="Кто совершил действие")
    action: Optional[str] = Field(None, description="Само действие с кассой")
    money: Optional[int] = Field(None, description="Количество денег (приход/расход)")


class AuditActionResponse(BaseModel):
    """Схема для отдачи данных строки на фронтенд.
    Используется внутри списка действий дня.
    """
    model_config = ConfigDict(from_attributes=True)  # Включаем чтение объектов SQLAlchemy

    id: int
    actor: str
    action: str
    money: int
    audit_day_id: int
    created_at: datetime