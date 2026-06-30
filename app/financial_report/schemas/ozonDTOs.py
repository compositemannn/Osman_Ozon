from pydantic import BaseModel, Field
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

# --- 1.1. Запрос к Ozon API ---
class OzonBuyoutReportRequest(BaseModel):
    """Схема для отправки запроса в Ozon на получение отчета о выкупах"""
    # Озон обычно требует фильтр по датам или конкретный период
    date: date = Field(..., description="День отчета")
    last_id: date = Field(..., description="Идентификатор последнего значения на странице")


# --- 1.2. Прием данных ИЗ Ozon API ---
class OzonTotalAmount(BaseModel):
    """Схема для итоговой суммы операции"""
    amount: str = Field(..., description="Чистая сумма к начислению/списанию строкой")
    currency: str = Field(..., description="Валюта операции")


class OzonAccrualItem(BaseModel):
    """Схема для одной финансовой операции из массива начислений Ozon"""
    accrued_category: str = Field(..., description="Категория начисления (например, DELIVERED_PRODUCTS)")
    unit_number: Optional[str] = Field(None, description="Номер отправления (posting_number в нашей БД)")
    total_amount: OzonTotalAmount = Field(..., description="Объект с деталями итоговой суммы")


class OzonAccrualReportResponse(BaseModel):
    """Схема для полного ответа, который возвращает нам Ozon API (начисления за день)"""
    accruals: List[OzonAccrualItem] = Field(..., description="Список начислений")
    last_id: str = Field(..., description="Идентификатор последней записи для пагинации")