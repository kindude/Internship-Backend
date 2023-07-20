from __future__ import annotations

import logging
from dotenv import load_dotenv
from sqlalchemy import select, delete, desc
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from models.User import User
from schemas.User import UserResponse, UsersListResponse, UserScheme
from schemas.pasword_hashing import hash

# Создание объекта логгера
logger = logging.getLogger(__name__)
load_dotenv()
class UserRepository:
    def __init__(self, database: async_sessionmaker[AsyncSession]):
        self.async_session = database

    async def create_user(self, request: UserScheme) -> User:
        try:
            hashed = hash(request.password)
            user = User(username=request.username, email=request.email, password=hashed, city=request.city,
                        country=request.country, phone=request.phone,
                        status=request.status, roles=request.roles)
            async with self.async_session as session:
                session.add(user)
                await session.commit()
                logger.info(f"New user created: {request.username}")
                return user

        except Exception as e:
            # Handle the specific exception here
            print(f"An error occurred while creating the user: {e}")
            raise e

    async def get_user(self, id: int) -> UserResponse:
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

    async def get_users(self, page: int = 1, per_page: int = 10) -> UsersListResponse:
        # Calculate the offset based on the page and per_page values
        offset = (page - 1) * per_page

        query = select(User).slice(offset, offset + per_page)
        users = await self.async_session.execute(query)
        user_list = [self.user_to_dict(user) for user in users.scalars().all()]
        return UsersListResponse(users=user_list)

    def user_to_dict(self, user) -> UserScheme:
        return UserScheme(
            id=user.id,
            username=user.username,
            email=user.email,
            city=user.city,
            password=user.password,
            country=user.country,
            phone=user.phone,
            status=user.status,
            roles=user.roles
        )

    async def del_user(self, user_id: int) -> bool:
        try:
            user = await self.get_user(user_id)
            if user:
                async with self.async_session as session:
                    query = delete(User).where(User.id == user_id)
                    result = await session.execute(query)
                    await session.commit()
                    if result:
                        logger.info(f"Пользователь удален: ID {user_id}")
                        return True
                    else:
                        return False
            else:
                return False

        except Exception as e:
            print(f"An error occurred while deleting user: {e}")

    async def update_user(self, id: int, username: str, email: str, password: str, city: str, country: str,
                          phone: str, status: bool, roles: list) -> UserResponse:
        try:
            async with self.async_session as session:
                user = await session.get(User, id)
                if user is not None:
                    user.username = username
                    user.email = email
                    user.password = hash(password)
                    user.city = city
                    user.country = country
                    user.phone = phone
                    user.status = status
                    user.roles = roles
                    await session.commit()
                    logger.info(f"User updated: ID {id}")
                    updated_roles = list(user.roles)

                    return UserResponse(
                        id=user.id,
                        username=user.username,
                        email=user.email,
                        password=user.password,
                        city=user.city,
                        country=user.country,
                        phone=user.phone,
                        status=user.status,
                        roles=updated_roles
                    )
        except Exception as e:
            print(f"An error occurred while updating user: {e}")

