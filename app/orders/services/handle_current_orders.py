from datetime import date

from app.orders.schemas.current_orders import OrdersDayResponseSchema


class CurrentOrdersHandler:
    def __init__(self, repo):
        self.repo = repo

    async def handle_get_orders_by_day(self, day: date):
        orders_from_db = await self.repo.get_orders_by_day(day)
        orders = OrdersDayResponseSchema.model_validate(orders_from_db)
        return orders
