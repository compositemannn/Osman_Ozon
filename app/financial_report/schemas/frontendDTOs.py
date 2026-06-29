from pydantic import BaseModel, Field
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

class FinancialReportQuery(BaseModel):
    """Схема параметров входящего GET-запроса от фронтенда"""
    target_date: date = Field(..., description="Дата, за которую запрашивается финансовый отчет")

# --- 3.1. Элементы таблиц (Строки) ---

class ExpectedOrderRow(BaseModel):
    """Строка Первой таблицы: Ожидаемые выплаты за сегодня"""
    posting_number: str
    last_event_time: datetime
    calculated_payout: Decimal  # Наш внутренний расчет (expected_payout минус отмены)
    is_red: bool                # True -> Доставлен сегодня, но Озон еще не выплатил за него сегодня

class RealPayoutRow(BaseModel):
    """Строка Второй таблицы: Реальные выплаты от Озона за сегодня"""
    posting_number: str
    last_event_time: datetime
    real_payout: Decimal        # Чистая сумма из поля order.payout
    is_green: bool              # True -> Оплачен сегодня, но дата доставки НЕ сегодняшняя ("хвост")

# --- 3.2. Сами таблицы с их внутренними итогами ---

class ExpectedTable(BaseModel):
    """Первая таблица в сборе"""
    orders: List[ExpectedOrderRow]
    total_all: Decimal   = Field(..., description="Итого: Сумма вообще ВСЕХ доставленных сегодня заказов")
    total_clean: Decimal = Field(..., description="Итого без красных: Сумма заказов, за которые сегодня РЕАЛЬНО пришла выплата")

class RealTable(BaseModel):
    """Вторая таблица в сборе"""
    orders: List[RealPayoutRow]
    total_all: Decimal   = Field(..., description="Итого: Сумма вообще ВСЕХ выплат, пришедших сегодня")
    total_clean: Decimal = Field(..., description="Итого без зеленых: Сумма выплат за заказы, которые были доставлены именно сегодня")

# --- 3.3. Главный финальный JSON-ответ ---

class FinancialReportResponse(BaseModel):
    """Итоговый ответ, который летит на фронтенд при GET-запросе"""
    target_date: date
    is_ozon_report_received: bool = Field(..., description="Флаг: пришел ли вообще сегодня отчет от Озона")
    expected_table: ExpectedTable
    real_table: RealTable