

from __future__ import annotations
import hashlib
import math
import os
import logging

from models.User import User
from dotenv import load_dotenv
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from schemas.User import UserResponse, UsersListResponse

# Создание объекта логгера
logger = logging.getLogger(__name__)
load_dotenv()
class UserRepository:
    def __init__(self, async_session: async_sessionmaker[AsyncSession]):
        self.async_session = async_session

    async def create_user(self, username, email, password, city, country, phone, status, roles) -> User:
        try:
            salt = os.getenv("SALT")
            database_password = password + salt
            hashed = hashlib.md5(database_password.encode()).hexdigest()
            user = User(username, email, hashed, city, country, phone, status, roles)
            self.session.add(user)
            await self.session.flush()
            logger.info(f"Создан новый пользователь: {username}")

        except Exception as e:
            # Handle the specific exception here
            print(f"An error occurred during user creation: {e}")

        return user

    async def get_user(self, id: int):
        async with self.async_session as session:
            query = select(User).filter(User.id == id)
            result = await session.execute(query)
            user = result.scalar_one_or_none()
            if user is None:
                return None

            return UserResponse(
                id=user.id,
                username=user.username,
                email=user.email,
                password=user.password,
                city=user.city,
                country=user.country,
                phone=user.phone,
                status=user.status,
                roles=user.roles,
            )

    import math


    async def get_users(self, page: int = 1, per_page: int = 10):
        query = select(User)
        users = await self.async_session.execute(query)
        user_list = [self.user_to_dict(user) for user in users.scalars().all()]
        return UsersListResponse(users=user_list)

    def user_to_dict(self, user):
        return {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'password': user.password,
            'city': user.city,
            'country': user.country,
            'phone': user.phone,
            'status': user.status,
            'roles': ','.join(user.roles)
        }




        # # Calculate the total number of pages
        # total_pages = math.ceil(count / per_page)
        #
        # # Adjust the page number if it exceeds the total pages
        # page = min(page, total_pages)
        #
        # # Calculate the offset and limit based on the page and per_page values
        # offset = (page - 1) * per_page
        # limit = per_page
        #
        # # Apply pagination to the query
        # query = query.offset(offset).limit(limit)
        #
        # # Execute the query and retrieve the users
        # result = await self.async_session.execute(query)
        # users = result.scalars().all()

        # return {
        #     'users': users,
        #     'page': page,
        #     'per_page': per_page,
        #     'total_pages': total_pages,
        #     'total_count': count
        # }

    async def del_user(self, user_id: int):
        try:
            user = await self.get_user(user_id)
            if user:
                await self.session.delete(user)
                await self.session.commit()
            logger.info(f"Пользователь удален: ID {user_id}")
        except Exception as e:
            print(f"An error occurred while deleting user: {e}")

    async def update_user(self, user_id: int, username: str, email: str, password: str, city: str, country: str,
                          phone: str, status: bool, roles: list):
        try:
            user = await self.get_user(user_id)
            if user:
                user.username = username
                user.email = email
                user.password = password
                user.city = city
                user.country = country
                user.phone = phone
                user.status = status
                user.roles = roles
                await self.session.commit()
                logger.info(f"Пользователь обновлен: ID {user_id}")
        except Exception as e:
            print(f"An error occurred while updating user: {e}")

