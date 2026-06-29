from pydantic import BaseModel, Field
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

# --- 1.1. Запрос к Ozon API ---
class OzonBuyoutReportRequest(BaseModel):
    """Схема для отправки запроса в Ozon на получение отчета о выкупах"""
    # Озон обычно требует фильтр по датам или конкретный период
    date_from: date = Field(..., description="Начало периода отчета")
    date_to: date = Field(..., description="Конец периода отчета")


# --- 1.2. Прием данных ИЗ Ozon API ---
class OzonBuyoutItem(BaseModel):
    """Схема для одного товара из массива ответа Ozon API"""
    sku: int
    posting_number: str
    name: str
    quantity: int
    amount: Decimal  # Чистая сумма к начислению за этот товар
    # Дополнительные поля из доки, если пригодятся в будущем:
    buyout_price: Optional[Decimal] = None
    seller_price_per_instance: Optional[Decimal] = None

class OzonBuyoutReportResponse(BaseModel):
    """Схема для полного ответа, который возвращает нам Ozon API (массив товаров)"""
    result: List[OzonBuyoutItem]