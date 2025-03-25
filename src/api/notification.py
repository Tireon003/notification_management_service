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
from fastapi.responses import JSONResponse
from sqlalchemy.exc import NoResultFound

from src.dependencies import notification_service
from src.exceptions import NotificationAlreadyReadError
from src.schemas import NotificationCreate, NotificationRead, Paginator
from src.services import NotificationService

router = APIRouter(
    prefix="/notification",
    tags=["notification"],
)


@router.post(
    path="/",
    description="Add a notification",
    status_code=status.HTTP_201_CREATED,
)
async def create_notification(
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
async def get_notifications(
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
async def get_notification(
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
async def get_notification_processing_status(
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
