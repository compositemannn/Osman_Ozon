from datetime import date

from fastapi import APIRouter, Depends

from ..repositories.dependencies import get_repo_current_orders_obj
from ..services.handle_current_orders import CurrentOrdersHandler

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("/")
async def get_orders_by_day(day: date, repo=Depends(get_repo_current_orders_obj)):
    handler = CurrentOrdersHandler(repo)
    return await handler.handle_get_orders_by_day(day)
