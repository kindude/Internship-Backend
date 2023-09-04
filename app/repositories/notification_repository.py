from typing import List

from fastapi import Depends
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from datetime import datetime
from db.get_db import get_db
from models.Models import Notification, Quiz
from repositories.action_repository import ActionRepository
from repositories.company_repository import CompanyRepository
from schemas.Quiz import DeleteScheme


class NotificationRepository:

    def __init__(self, session: AsyncSession):
        self.session = session


    async def create_notifications(self, company_id: int, quiz_id:int) -> List[Notification]:

        action_repository = ActionRepository(database=self.session)
        users = await action_repository.get_users_in_company(company_id=company_id)
        notifications = []
        for user in users.users:
            notification = Notification(
                status="UNREAD",
                text=f"New quiz for company {company_id} has been created",
                user_id=user.id,
                timestamp=datetime.utcnow()
            )
            notifications.append(notification)
            self.session.add(notification)
            await self.session.commit()
        return notifications

    async def get_notification(self, notification_id: int) -> Notification:
        query = select(Notification).filter(Notification.id == notification_id)
        notification = await self.session.execute(query)
        notification = notification.scalar_one_or_none()
        return notification

    async def get_notifications(self, user_id: int) -> List[Notification]:
        action_repo = ActionRepository(database=self.session)
        query = (
            select(Notification).filter(and_(Notification.user_id == user_id),Notification.status == "UNREAD")
        )
        notifications = await self.session.execute(query)
        notifications = notifications.scalars().all()
        return notifications

    async def update_notification(self, notification_id: int, status: str) -> Notification:
        notification = await self.get_notification(notification_id=notification_id)
        if notification:
            notification.status = status
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


