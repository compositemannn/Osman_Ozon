from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.audit.routers.audit_router import router as audit_router
from app.financial_report.routers.report_router import router as report_router

# Импортируем наш настроенный планировщик
from app.financial_report.services.scheduler import scheduler
from app.notifications.routers.notifications import router as notifications_router
from app.orders.routers.current_orders import router as current_orders_router

from .audit.routers.audit_router import router as audit_router
from .notifications.routers.notifications import router as notifications_router
from .orders.routers.current_orders import router as current_orders_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Действия при СТАРТЕ сервера ---
    print("[Lifespan] Запуск фонового планировщика задач...")
    scheduler.start()

    yield  # В этой точке FastAPI запускается и начинает принимать запросы

    # --- Действия при ОСТАНОВКЕ сервера ---
    print("[Lifespan] Остановка фонового планировщика задач...")
    scheduler.shutdown()


# Передаем созданный lifespan в конструктор FastAPI
app = FastAPI(title="Gorbushka Keepers Ozon", version="1.0.0", lifespan=lifespan)

# Подключаем твои роутеры
app.include_router(notifications_router)
app.include_router(current_orders_router)
app.include_router(audit_router)


@app.get("/")
def ping():
    return {"message": "OK"}
