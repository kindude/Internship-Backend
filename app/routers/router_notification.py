import starlette
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from db.get_db import get_db
from models.Models import Notification
from repositories.notification_repository import NotificationRepository
from schemas.Notification import NotificationResponse, NotificationListResponse
from schemas.User import UserResponse
from utils.auth import get_current_user

router_notification = APIRouter()
def notification_to_response( notification: Notification) -> NotificationResponse:
    return NotificationResponse(
        id=notification.id,
        timestamp=notification.timestamp,
        text=notification.text,
        status=notification.status,
        quiz_id=notification.quiz_id
    )


@router_notification.put("/user/notification/{notif_id}/update", tags=["User-notification"])
async def update_user_notification(notif_id:int, db:AsyncSession = Depends(get_db), current_user: UserResponse = Depends(get_current_user)):
    notif_repo = NotificationRepository(session=db)
    notification = await notif_repo.update_notification(notification_id=notif_id, status="READ")
    return status.HTTP_200_OK

@router_notification.get("/user/notifications/get", tags=["User-notification"])
async def get_user_notifications(db:AsyncSession = Depends(get_db), current_user: UserResponse = Depends(get_current_user)):
    notif_repo = NotificationRepository(session=db)
    notifications = await notif_repo.get_notifications(user_id=current_user.id)
    return notifications



