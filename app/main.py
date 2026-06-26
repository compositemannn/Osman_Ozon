from fastapi import FastAPI

from .notifications.routers.notifications import router as notifications_router
from .orders.routers.current_orders import router as current_orders_router

app = FastAPI(
    title="Gorbushka Keepers Ozon",
    version="1.0.0",
)

app.include_router(notifications_router)
app.include_router(current_orders_router)


@app.get("/")
def ping():
    return {"message": "OK"}
