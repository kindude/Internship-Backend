from typing import List

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from datetime import datetime
from db.get_db import get_db
from models.Models import Notification, Quiz
from repositories.action_repository import ActionRepository
from schemas.Quiz import DeleteScheme


class NotificationRepository:

    def __init__(self, session: AsyncSession):
        self.session = session


    async def create_notification(self, company_id: int, quiz_id:int) -> Notification:
        notification = Notification(
            status="UNREAD",
            text=f"New quiz for company {company_id} has been created",
            quiz_id=quiz_id,
            timestamp=datetime.utcnow()
        )

        self.session.add(notification)
        await self.session.commit()
        return notification

    async def get_notification(self, notification_id: int) -> Notification:
        query = select(Notification).filter(Notification.id == notification_id)
        notification = await self.session.execute(query)
        notification = notification.scalar_one_or_none()
        return notification

    async def get_notifications(self, user_id: int, company_id: int) -> List[Notification]:
        action_repo = ActionRepository(database=self.session)
        if action_repo.if_member(user_id=user_id, company_id=company_id):
            query = (
                select(Notification)
                .join(Quiz)
                .options(selectinload(Notification.quiz))
                .where(Quiz.company_id == company_id)
            )
            notifications = await self.session.execute(query)
            notifications = notifications.scalars().all()
            return notifications

    async def update_notification(self, notification_id: int, status: str, text: str) -> Notification:
        notification = await self.get_notification(notification_id=notification_id)
        if notification:
            notification.status = status
            notification.text = text
            await self.session.commit()
            return notification

    async def delete_notification(self, notification_id:int) -> DeleteScheme:
        notification = await self.get_notification(notification_id=notification_id)
        await self.session.delete(notification)
        await self.session.commit()
        return DeleteScheme(
            id=notification_id,
            message="Notification was deleted"
        )


