from datetime import date, datetime
from typing import List, Optional
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field
from app.audit.schemas.AuditActionDTOs import  AuditActionResponse


class AuditDayResponse(BaseModel):
    """Базовая схема для дня (без списка вложенных действий)."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    date: date
    initial_cash: int = Field(default=0, description="Деньги в кассе на начало дня")
    created_at: datetime

class AuditDayFullResponse(BaseModel):
    """Полная схема для загрузки страницы кассы за выбранный день (GET /api/audit/{date}).
    Собирает всю таблицу: верхнюю строку, массив действий, нижнюю строку и защиту.
    """
    model_config = ConfigDict(from_attributes=True)

    id: int
    date: date
    initial_cash: int = Field(default=0, description="Деньги в кассе на начало дня (верхняя строка)")
    
    # Вложенный список всех действий за этот день
    actions: List[AuditActionResponse] = Field(default=[], description="Действия за день")
    
    # Вычисляемые на бэкенде поля (их нет в таблице audit_days БД, они считаются на лету)
    final_cash: int = Field(..., description="Деньги в кассе в конце дня (нижняя строка)")
    is_editable: bool = Field(..., description="Флаг защиты: можно ли редактировать этот день (False для будущего)")