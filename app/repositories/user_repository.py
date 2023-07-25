from __future__ import annotations

import datetime
import logging

from dotenv import load_dotenv
from sqlalchemy import select, delete, desc
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from models.User import User
from schemas.User import UserResponse, UsersListResponse, UserScheme, UserDeleteScheme, UserLogin, Token
from schemas.pasword_hashing import hash, hash_with_salt
from utils.auth import create_token

# Создание объекта логгера
logger = logging.getLogger(__name__)
load_dotenv()


class UserRepository:

    def __init__(self, database: async_sessionmaker[AsyncSession]):
        self.async_session = database

    async def create_user(self, request: UserScheme) -> User:
        try:
            hashed = hash_with_salt(password=request.password)
            request.password = hashed
            user_dict = request.dict()
            user = User(**user_dict)
            async with self.async_session as session:
                session.add(user)
                await session.commit()
                logger.info(f"New user created: {request.username}")
                return user
        except Exception as e:
            print(f"An error occurred while creating the user: {e}")
            raise e

    async def get_user(self, id: int) -> UserResponse:
        async with self.async_session as session:
            query = select(User).filter(User.id == id)
            result = await session.execute(query)
            user = result.scalar_one_or_none()
            if user is None:
                return None
            return user

    async def get_users(self, page: int = 1, per_page: int = 10) -> UsersListResponse:
        offset = (page - 1) * per_page
        query = select(User).slice(offset, offset + per_page)
        users = await self.async_session.execute(query)
        user_list = [self.user_to_scheme(user) for user in users.scalars().all()]
        return UsersListResponse(users=user_list)

    def user_to_scheme(self, user: User) -> UserScheme:
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

    async def del_user(self, id: int) -> UserDeleteScheme:
        try:
            user = await self.get_user(id=id)
            if user:
                async with self.async_session as session:
                    query = delete(User).where(User.id == id)
                    result = await session.execute(query)
                    await session.commit()
                    if result:
                        logger.info(f"Пользователь удален: ID {id}")
                        return UserDeleteScheme(
                            message="User was successfully deleted",
                            id=id
                        )
                    else:
                        return UserDeleteScheme(
                            message="User wasn't deleted",
                            id=-1
                        )
            else:
                return UserDeleteScheme(
                    message="User wasn't deleted",
                    id=-1
                )

        except Exception as e:
            print(f"An error occurred while deleting user: {e}")

    async def update_user(self, id: int, request: UserScheme) -> UserResponse:
        try:
            async with self.async_session as session:
                user = await session.get(User, id)
                if user is not None:
                    user.username = request.username
                    user.email = request.email
                    user.password = hash(password=request.password)
                    user.city = request.city
                    user.country = request.country
                    user.phone = request.phone
                    user.status = request.status
                    user.roles = request.roles
                    await session.commit()
                    logger.info(f"User updated: ID {id}")
                    return user
        except Exception as e:
            print(f"An error occurred while updating user: {e}")

    async def get_user_by_username(self, email: str) -> UserResponse:
        try:
            async with self.async_session as session:
                query = select(User).filter(User.email == email)
                result = await session.execute(query)
                user = result.scalar_one_or_none()
                if user is None:
                    return None
                else:
                    return UserResponse(
                        id=user.id,
                        username=user.username,
                        email=user.email,
                        password=user.password,
                        city=user.password,
                        country=user.country,
                        phone=user.phone,
                        status=user.status,
                        roles=user.roles
                    )
                    return user
        except Exception as e:
            print(f"An error occurred while creating the user: {e}")
            raise e

    async def get_user_by_email(self, email: str) -> UserResponse:
        try:
            async with self.async_session as session:
                query = select(User).filter(User.email == email)
                result = await session.execute(query)
                user = result.scalar_one_or_none()
                if user is None:
                    return None
                else:
                    return user
        except Exception as e:
            print(f"An error occurred while creating the user: {e}")
            raise e

    def create_password(self):
        password = str(datetime.datetime.utcnow())
        pass_hashed = hash_with_salt(password=password)
        return pass_hashed