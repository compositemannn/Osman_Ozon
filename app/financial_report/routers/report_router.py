from fastapi import APIRouter, HTTPException, Query, Depends, status
from app.financial_report.services.handle_report import ReportHandle
from app.financial_report.schemas.frontendDTOs import FinancialReportResponse
from app.financial_report.repositories.dependencies import get_repo_obj
from app.financial_report.repositories.report_repo import ReportRepository
from datetime import date
import httpx
from app.infrastructure.config import settings
from app.financial_report.schemas.ozonDTOs import (
    OzonBuyoutReportRequest,
    OzonAccrualItem,
    OzonAccrualReportResponse,
    OzonTotalAmount
)

router = APIRouter(prefix="/report", tags=["report"])

@router.get("", response_model=FinancialReportResponse)
async def get_financial_report(
    target_date: date = Query(..., description="Дата отчета в формате YYYY-MM-DD"), 
    repo: ReportRepository = Depends(get_repo_obj)
):
    try:
        service = ReportHandle(repo=repo)
        response = await service.get_financial_report(target_date=target_date)
        return response
    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера при сборке финансового отчета."
        )

@router.post("/sync-ozon")
async def sync_ozon_report(
    target_date: date = Query(..., description="Дата для синхронизации начислений в формате YYYY-MM-DD"),
    repo: ReportRepository = Depends(get_repo_obj)
):
    """
    Запрашивает начисления за конкретный день из Ozon API,
    обрабатывает постраничную пагинацию через last_id и отправляет данные в хэндлер.
    """
    headers = {
        "Client-Id": settings.CLIENT_ID,
        "Api-Key": settings.API_KEY,
        "Content-Type": "application/json"
    }

    current_last_id = ""
    has_more_pages = True
    total_db_updated = False
    service = ReportHandle(repo=repo)

    async with httpx.AsyncClient(base_url="https://api-seller.ozon.ru") as client:
        while has_more_pages:
            # Формируем тело запроса строго по спецификации эндпоинта /v1/finance/accrual/by-day
            payload = {
                "date": target_date.strftime("%Y-%m-%d"),
                "last_id": current_last_id
            }

            try:
                response = await client.post("/v1/finance/accrual/by-day", json=payload, headers=headers)
                
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Ozon API вернул статус-код: {response.status_code}"
                    )
                    
                raw_json = response.json()
                
                # Валидируем текущую страницу через новую вложенную Pydantic-схему
                ozon_response_dto = OzonAccrualReportResponse(**raw_json)

            except HTTPException:
                raise
            except httpx.HTTPError as net_err:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"Ошибка сети при обращении к Ozon API: {str(net_err)}"
                )
            except Exception as val_err:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Не удалось распарсить структуру ответа Ozon: {str(val_err)}"
                )

            # Отправляем валидированные данные текущей страницы в хэндлер
            page_updated = await service.update_payouts_from_ozon_data(
                ozon_data=ozon_response_dto, 
                report_date=target_date
            )
            
            if page_updated:
                total_db_updated = True

            # Проверяем пагинацию: если Ozon вернул непустой last_id, используем его для следующего шага
            if ozon_response_dto.last_id:
                current_last_id = ozon_response_dto.last_id
            else:
                has_more_pages = False  # Когда выкачали все страницы, Ozon вернет пустую строку

    if not total_db_updated:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT,
            detail="Новых начислений по доставкам за этот день не обнаружено."
        )

    return {"status": "success", "message": f"Все начисления за {target_date} успешно синхронизированы с БД"}