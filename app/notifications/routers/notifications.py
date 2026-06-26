from typing import Any

from fastapi import APIRouter, Body, Depends, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from ..repositories.dependencies import get_repo_obj
from ..schemas.notification_dtos import NotificationTypeEnum
from ..services.handle_notifications import NotificationHandler

router = APIRouter(tags=["webhook"])


@router.post("/notification")
async def handle_ozon_webhook(
    payload: dict[str, Any] = Body(...), repo=Depends(get_repo_obj)
):

    try:
        notification_type: NotificationTypeEnum = payload.get("message_type")  # pyright: ignore[reportAssignmentType]
        handler = NotificationHandler(payload=payload, repo=repo)

        await handler.notification_distribution(notification_type=notification_type)

        # if payload.get("message_type") == notification_schemas.NotificationTypeEnum.TYPE_PING:
        #     dto = notification_schemas.OzonPingNotificationDTO.model_validate(payload)
        #     return JSONResponse(
        #         status_code=status.HTTP_200_OK,
        #         content={
        #             "version": "string",
        #             "name": "string",
        #             "time": dto.time.isoformat()
        #         }
        #     )

        # elif payload.get("message_type") == notification_schemas.NotificationTypeEnum.TYPE_NEW_POSTING:
        #     dto = notification_schemas.OrderCreatedNotificationDTO.model_validate(payload)
        #     await create_order_with_items(session, dto)

        # elif payload.get("message_type") == notification_schemas.NotificationTypeEnum.TYPE_STATE_CHANGED:
        #     dto = notification_schemas.OrderUpdatedStatusNotificationDTO.model_validate(payload)
        #     await update_order_status(session, dto)

    except ValidationError as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": {
                    "code": "ERROR_PARAMETER_VALUE_MISSED",
                    "message": "Пропущен необходимый параметр",
                    "details": str(e),
                }
            },
        )

    return JSONResponse(status_code=200, content={"result": True})
