import asyncio
from typing import Annotated
from uuid import UUID

from fastapi import (
    APIRouter,
    status,
    Body,
    Query,
    Depends,
    Path,
    HTTPException,
)
from fastapi.encoders import jsonable_encoder
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from fastapi_cache.decorator import cache
from sqlalchemy.exc import NoResultFound
from starlette.websockets import WebSocket, WebSocketDisconnect

from src.dependencies import notification_service
from src.exceptions import NotificationAlreadyReadError
from src.schemas import NotificationCreate, NotificationRead, Paginator
from src.services import NotificationService
from src.utils import key_builder_by_url_method
from src.limiter import limiter

router = APIRouter(
    prefix="/notification",
    tags=["notification"],
)


@router.post(
    path="/",
    description="Add a notification",
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("2/second")
async def create_notification(
    request: Request,
    notification_data: Annotated[
        NotificationCreate,
        Body(),
    ],
    service: Annotated[
        NotificationService,
        Depends(notification_service),
    ],
) -> NotificationRead:

    new_notification = await service.create_notification(notification_data)

    return new_notification


@router.get(
    path="/",
    description="Get all notifications",
    status_code=status.HTTP_200_OK,
)
@limiter.limit("6/minute")
async def get_notifications(
    request: Request,
    paginator: Annotated[
        Paginator,
        Query(),
    ],
    service: Annotated[
        NotificationService,
        Depends(notification_service),
    ],
) -> list[NotificationRead]:
    notifications = await service.get_notifications(paginator)
    return notifications


@router.get(
    path="/{notification_id}",
    description="Get detailed info about concrete notification",
    status_code=status.HTTP_200_OK,
)
@limiter.limit("1/second")
@cache(expire=20, key_builder=key_builder_by_url_method)
async def get_notification(
    request: Request,
    notification_id: Annotated[UUID, Path()],
    service: Annotated[
        NotificationService,
        Depends(notification_service),
    ],
) -> NotificationRead:
    try:
        notification = await service.get_notification(notification_id)
        return notification
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error while getting notification: {exc}. Please, contact with dev and provide this detail.",
        )


@router.patch(
    path="/{notification_id}/read",
    description="Set notification read",
    status_code=status.HTTP_200_OK,
)
async def set_notification_read(
    notification_id: Annotated[UUID, Path()],
    service: Annotated[
        NotificationService,
        Depends(notification_service),
    ],
) -> NotificationRead:
    try:
        refreshed_notification = await service.read_notification(
            notification_id
        )
        return refreshed_notification
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )
    except NotificationAlreadyReadError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{exc}",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error while getting notification: {exc}. Please, contact with dev and provide this detail.",
        )


@router.get(
    path="/{notification_id}/processing_status",
    status_code=status.HTTP_200_OK,
    description="Get current notification analyze status",
)
@limiter.limit("1/second")
@cache(expire=5, key_builder=key_builder_by_url_method)
async def get_notification_processing_status(
    request: Request,
    notification_id: Annotated[UUID, Path()],
    service: Annotated[
        NotificationService,
        Depends(notification_service),
    ],
) -> JSONResponse:
    try:
        notification = await service.get_notification(notification_id)
        return JSONResponse(
            content=dict(status=notification.processing_status),
            status_code=status.HTTP_200_OK,
        )
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error while getting notification: {exc}. Please, contact with dev and provide this detail.",
        )


@router.websocket(path="/stream")
async def get_notifications_realtime(
    websocket: WebSocket,
    service: Annotated[
        NotificationService,
        Depends(notification_service),
    ],
) -> None:
    await websocket.accept()
    while True:
        await asyncio.sleep(1)
        try:
            recent_notifications = await service.get_recent_notifications()
            notifications_data = jsonable_encoder(recent_notifications)
            await websocket.send_json(notifications_data)
        except WebSocketDisconnect:
            return
