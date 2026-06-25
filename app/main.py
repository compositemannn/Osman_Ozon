from fastapi import FastAPI

from .notifications.routers.notifications import router as notification_order

app = FastAPI(
    title="Gorbushka Keepers Ozon",
    version="1.0.0",
)

app.include_router(notification_order)


@app.get("/")
def ping():
    return {"message": "OK"}
