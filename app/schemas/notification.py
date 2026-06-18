from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, field_validator
from decimal import Decimal


class NotificationTypeEnum(str, Enum):
    TYPE_PING = "TYPE_PING"
    TYPE_NEW_POSTING = "TYPE_NEW_POSTING"
    TYPE_STATE_CHANGED = "TYPE_STATE_CHANGED"
    TYPE_STOCKS_CHANGED = "TYPE_STOCKS_CHANGED"


class OrderUpdatedStatusEnum(str, Enum):
    posting_acceptance_in_progress = "posting_acceptance_in_progress"
    posting_created = "posting_created"
    posting_awaiting_registration = "posting_awaiting_registration"
    posting_transferring_to_delivery = "posting_transferring_to_delivery"
    posting_in_carriage = "posting_in_carriage"
    posting_not_in_carriage = "posting_not_in_carriage"
    posting_in_arbitration = "posting_in_arbitration"
    posting_in_client_arbitration = "posting_in_client_arbitration"
    posting_on_way_to_city = "posting_on_way_to_city"
    posting_transferred_to_courier_service = "posting_transferred_to_courier_service"
    posting_in_courier_service = "posting_in_courier_service"
    posting_on_way_to_pickup_point = "posting_on_way_to_pickup_point"
    posting_in_pickup_point = "posting_in_pickup_point"
    posting_conditionally_delivered = "posting_conditionally_delivered"
    posting_driver_pick_up = "posting_driver_pick_up"
    posting_delivered = "posting_delivered"
    posting_received = "posting_received"
    posting_canceled = "posting_canceled"
    posting_not_in_sort_center = "posting_not_in_sort_center"


STATUS_LABELS: dict[OrderUpdatedStatusEnum, str] = {
    OrderUpdatedStatusEnum.posting_acceptance_in_progress: "Идёт приёмка",
    OrderUpdatedStatusEnum.posting_awaiting_registration: "Ожидает регистрации",
    OrderUpdatedStatusEnum.posting_transferring_to_delivery: "Передаётся в доставку",
    OrderUpdatedStatusEnum.posting_in_carriage: "В перевозке",
    OrderUpdatedStatusEnum.posting_created: "Создан",
    OrderUpdatedStatusEnum.posting_not_in_carriage: "Не добавлен в перевозку",
    OrderUpdatedStatusEnum.posting_in_arbitration: "Арбитраж",
    OrderUpdatedStatusEnum.posting_in_client_arbitration: "Клиентский арбитраж",
    OrderUpdatedStatusEnum.posting_on_way_to_city: "На пути в ваш город",
    OrderUpdatedStatusEnum.posting_transferred_to_courier_service: "Передаётся курьеру",
    OrderUpdatedStatusEnum.posting_in_courier_service: "Курьер в пути",
    OrderUpdatedStatusEnum.posting_on_way_to_pickup_point: "На пути в пункт выдачи",
    OrderUpdatedStatusEnum.posting_in_pickup_point: "В пункте выдачи",
    OrderUpdatedStatusEnum.posting_conditionally_delivered: "Условно доставлено",
    OrderUpdatedStatusEnum.posting_driver_pick_up: "У водителя",
    OrderUpdatedStatusEnum.posting_delivered: "Доставлено",
    OrderUpdatedStatusEnum.posting_received: "Получено",
    OrderUpdatedStatusEnum.posting_canceled: "Отменено",
    OrderUpdatedStatusEnum.posting_not_in_sort_center: "Не принято на сортировочном центре"
}


# --- БАЗОВАЯ МОДЕЛЬ (Только общее для всех поле) ---

class OzonBaseWebhook(BaseModel):
    message_type: NotificationTypeEnum




# Схема для TYPE_PING
class OzonPingNotificationDTO(OzonBaseWebhook):
    time: datetime


# Схемы для TYPE_NEW_POSTING
class OrderCreatedItemsDTO(BaseModel):
    sku: int
    offer_id: str
    quantity: int
    price: Decimal
    payout: Decimal
    commission_amount: Decimal

class OrderCreatedNotificationDTO(OzonBaseWebhook):
    posting_number: str
    seller_id: int
    products: List[OrderCreatedItemsDTO]
    in_process_at: Optional[datetime] = None  # Из-за сноски Ozon: может быть пустым при поздней оплате
    warehouse_id: int
    shipment_date: datetime
    tpl_integration_type: str
    is_express: bool
    tracking_number: Optional[str] = None
    delivery_date_begin: datetime
    delivery_date_end: datetime


# Схема для TYPE_STATE_CHANGED
class OrderUpdatedStatusNotificationDTO(OzonBaseWebhook):
    posting_number: str
    new_state: OrderUpdatedStatusEnum
    changed_state_date: datetime
    seller_id: int
    @field_validator("changed_state_date", mode="after")
    @classmethod
    def ensure_utc(cls, v: datetime) -> datetime:
        # Если дата пришла без таймзоны (naive), принудительно говорим, что это UTC
        if v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        
        # Если дата пришла с другой таймзоной (например, +03:00), 
        # она автоматически пересчитается в эквивалентное время UTC
        return v.astimezone(timezone.utc)



# Схемы для TYPE_STOCKS_CHANGED (По вложенности)
class StockWarehouseItem(BaseModel):
    warehouse_id: int
    present: int
    reserved: int

class StockProductItem(BaseModel):
    product_id: int
    sku: int
    updated_at: datetime
    stocks: List[StockWarehouseItem]

class OrderStocksNotificationDTO(OzonBaseWebhook):
    seller_id: int
    items: List[StockProductItem]
