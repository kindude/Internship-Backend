from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.get_db import get_db
from models.Models import Notification
from repositories.notification_repository import NotificationRepository
from schemas.Notification import NotificationResponse, NotificationListResponse

router_notification = APIRouter()
def notification_to_response( notification: Notification) -> NotificationResponse:
    return NotificationResponse(
        id=notification.id,
        timestamp=notification.timestamp,
        text=notification.text,
        status=notification.status,
        quiz_id=notification.quiz_id
    )


@router_notification.get("/notification/get/{notif_id}")
async def get_notification(notif_id:int, db:AsyncSession = Depends(get_db)) -> NotificationResponse:
    notif_rep = NotificationRepository(session=db)
    notification = await notif_rep.get_notification(notification_id=notif_id)
    return notification_to_response(notification=notification)

@router_notification.get("company/{company_id}/notification/get/")
async def get_notifications(company_id:int, db:AsyncSession = Depends(get_db)) -> NotificationListResponse:
    notif_rep = NotificationRepository(session=db)
    notifications = await notif_rep.get_notifications(company_id=company_id)
    notifications = [notification_to_response(notif) for notif in notifications]
    return NotificationListResponse(notifications=notifications)



