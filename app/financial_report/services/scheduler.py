from datetime import date, timedelta
import httpx
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.infrastructure.config import settings
# Импортируем фабрику сессий напрямую
from app.infrastructure.database import async_session_maker 

from app.financial_report.services.handle_report import ReportHandle
from app.financial_report.schemas.ozonDTOs import OzonAccrualReportResponse
from app.financial_report.repositories.report_repo import ReportRepository

async def sync_ozon_job():
    """
    Фоновая задача: запускается сама по себе внутри процесса,
    самостоятельно открывает сессию к БД и обновляет начисления Ozon за вчера и сегодня.
    """
    headers = {
        "Client-Id": settings.CLIENT_ID,
        "Api-Key": settings.API_KEY,
        "Content-Type": "application/json"
    }

    today = date.today()
    # Берем окно в 2 дня, чтобы точно закрыть задержки со стороны Ozon
    target_dates = [today - timedelta(days=1), today]

    # Вот тут руками открываем сессию, так как Depends() здесь не работает
    async with async_session_maker() as session:
        # Передаем сессию в конструктор репозитория
        repo = ReportRepository(session=session)
        service = ReportHandle(repo=repo)

        async with httpx.AsyncClient(base_url="https://api-seller.ozon.ru") as client:
            for target_date in target_dates:
                current_last_id = ""
                has_more_pages = True
                date_str = target_date.strftime("%Y-%m-%d")

                while has_more_pages:
                    payload = {
                        "date": date_str,
                        "last_id": current_last_id
                    }

                    try:
                        response = await client.post("/v1/finance/accrual/by-day", json=payload, headers=headers)
                        if response.status_code != 200:
                            break
                            
                        raw_json = response.json()
                        ozon_response_dto = OzonAccrualReportResponse(**raw_json)

                        # Передаем страницу в хэндлер для сохранения в БД
                        await service.update_payouts_from_ozon_data(
                            ozon_data=ozon_response_dto, 
                            report_date=target_date
                        )

                        if ozon_response_dto.last_id:
                            current_last_id = ozon_response_dto.last_id
                        else:
                            has_more_pages = False

                    except Exception:
                        # Если одна страница упала, выходим из цикла текущей даты
                        break
        
        # Как только выходим из блока 'async with', сессия автоматически делает коммит и закрывается
        await session.commit()

# Инициализируем планировщик
scheduler = AsyncIOScheduler()

# Настраиваем интервал запуска: каждые 4 часа
scheduler.add_job(sync_ozon_job, "interval", hours=4, id="sync_ozon_every_4h")