from datetime import date, datetime
from decimal import Decimal
from app.financial_report.schemas.frontendDTOs import (
    FinancialReportQuery,
    FinancialReportResponse,
    RealPayoutRow,
    RealTable,
    ExpectedOrderRow,
    ExpectedTable
)
from app.financial_report.schemas.ozonDTOs import (
    OzonBuyoutReportRequest,
    OzonAccrualItem,
    OzonAccrualReportResponse,
    OzonTotalAmount
)


class ReportHandle:
    def __init__(self, repo):
        self.repo = repo

    async def get_financial_report(self, target_date: date) -> FinancialReportResponse:
        orders = await self.repo.get_financial_orders(target_date)

        expected_rows = []
        real_rows = []
        expected_total_all = Decimal("0.00")
        expected_total_clean = Decimal("0.00")
        real_total_all = Decimal("0.00")
        real_total_clean = Decimal("0.00")

        for order in orders:
            if not order.last_event_time: 
                continue

            if order.status == "delivered" and order.last_event_time.date() == target_date:
                order_calculated_payout = Decimal("0.00")
                for item in order.items:
                    # Находим количество реально выкупленного товара
                    real_quantity = item.quantity - item.quantity_cancelled
                    if real_quantity <= 0:
                        # Если весь товар в этой позиции отменен, то пропуск
                        continue
                    elif real_quantity > 0 and item.quantity > 0:
                        payout_per_unit = Decimal(str(item.expected_payout)) / Decimal(item.quantity)
                        order_calculated_payout += payout_per_unit * Decimal(real_quantity)
                
                order_calculated_payout = order_calculated_payout.quantize(Decimal("0.01")) 
                # Проверяем флаг "красный": если выплата еще не пришла или пришла не сегодня
                is_red = (order.payout_date is None) or (order.payout_date.date() != target_date)
                
                # Создаем строку ожидаемых выплат
                row = ExpectedOrderRow(
                    posting_number=order.posting_number,
                    last_event_time=order.last_event_time,
                    calculated_payout=order_calculated_payout.quantize(Decimal("0.01")),
                    is_red=is_red
                )
                expected_rows.append(row)
                
                # Плюсуем в общие итоги первой таблицы
                expected_total_all += order_calculated_payout
                if not is_red:
                    expected_total_clean += order_calculated_payout
            
            if order.payout_date and order.payout_date.date() == target_date:
                if not order.last_event_time: 
                    continue
                # Проверяем флаг "зеленый": если оплата пришла сегодня, но доставлен был в другой день
                is_green = order.last_event_time.date() != target_date

                # ЗАЩИТА: Гарантируем, что выплата — это Decimal, даже если в БД лежит float или None
                safe_payout = Decimal(str(order.payout)) if order.payout else Decimal("0.00")

                # Создаем строку реальных выплат
                row = RealPayoutRow(
                    posting_number=order.posting_number,
                    last_event_time=order.last_event_time,
                    real_payout=safe_payout.quantize(Decimal("0.01")) if safe_payout else Decimal("0.00"),
                    is_green=is_green
                )
                real_rows.append(row)
                
                # Плюсуем в общие итоги второй таблицы
                real_total_all += safe_payout
                if not is_green:
                    real_total_clean += safe_payout
        
        # Формируем финальный ответ для фронтенда
        return FinancialReportResponse(
            target_date=target_date,
            is_ozon_report_received=len(real_rows) > 0,
            expected_table=ExpectedTable(
                orders=expected_rows,
                total_all=expected_total_all.quantize(Decimal("0.01")),
                total_clean=expected_total_clean.quantize(Decimal("0.01"))
            ),
            real_table=RealTable(
                orders=real_rows,
                total_all=real_total_all.quantize(Decimal("0.01")),
                total_clean=real_total_clean.quantize(Decimal("0.01"))
            )
        )
    
    async def update_payouts_from_ozon_data(self, ozon_data: OzonAccrualReportResponse, report_date: date) -> bool:
        """
        Принимает одну валидированную страницу начислений Ozon API,
        фильтрует успешные доставки (выкупы) и обновляет информацию в БД.
        Returns:
            bool: True, если на этой странице был успешно обновлен хотя бы один заказ.
        """
       # Если массив начислений на текущей странице пустой, ловить нечего
        if not ozon_data.accruals:
            return False

        # Флаг для отслеживания, обновили ли мы хотя бы один заказ
        any_updated = False

        # Проходимся по каждой финансовой операции на странице
        for accrual in ozon_data.accruals:
            # Нас интересуют только реальные начисления за доставленные товары (выкупы)
            if accrual.accrued_category != "DELIVERED_PRODUCTS":
                continue
                
            # unit_number — это номер отправления (posting_number в нашей БД)
            posting_number = accrual.unit_number
            if not posting_number:
                continue

            # Достаем сумму из вложенного объекта total_amount (она там строкой)
            raw_amount = accrual.total_amount.amount
            payout_amount = Decimal(raw_amount)

            # Вызываем рабочий метод репозитория
            await self.repo.update_order_payout(
                posting_number=posting_number,
                payout_amount=payout_amount,
                payout_date=report_date
            )
            any_updated = True

        return any_updated
    