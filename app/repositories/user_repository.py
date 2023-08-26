from __future__ import annotations

import datetime
import logging
from math import ceil

from dotenv import load_dotenv
from sqlalchemy import select, delete, desc
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from models.Models import User, Action, Company
from schemas.Action import ActionResponse, ActionListResponse, ActionScheme
from schemas.Quiz import DeleteScheme
from schemas.User import UserResponse, UsersListResponse, UserScheme, UserDeleteScheme, UserLogin, Token, \
    UserResponseNoPass
from schemas.pasword_hashing import hash_with_salt
from utils.create_token import create_token

logger = logging.getLogger(__name__)
load_dotenv()


def action_to_resposne(action: Action) -> ActionResponse:
    return ActionResponse(
        user_id=action.user_id,
        company_id=action.company_id,
        status=action.status,
        type_of_action=action.type_of_action
    )

def action_to_scheme(action: Action) -> ActionScheme:
    return ActionScheme(
        id=action.id,
        user_id=action.user_id,
        company_id=action.company_id,
        status=action.status,
        type_of_action=action.type_of_action
    )

def user_to_response(user: User) -> UserResponse:
    return UserResponse(
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


class UserRepository:

    def __init__(self, database: AsyncSession):
        self.async_session = database

    async def authenticate_user(self, request: UserLogin) -> Token:
        try:
            user = await self.get_user_by_email(email=request.email)
            hashed_request_password = hash_with_salt(request.password)
            if hashed_request_password == user.password:
                token = create_token(user)
                return Token(
                    token=token
                )
            else:
                return False
        except Exception as e:
            print(f"An error occurred while creating the user: {e}")
            raise e

    async def create_user(self, request: UserScheme) -> User:
        try:
            hashed = hash_with_salt(password=request.password)
            request.password = hashed
            user_dict = request.dict()
            user = User(**user_dict)
            self.async_session.add(user)
            await self.async_session.commit()
            logger.info(f"New user created: {request.username}")
            return user
        except Exception as e:
            print(f"An error occurred while creating the user: {e}")
            raise e

    async def get_user(self, id: int) -> UserResponseNoPass:
            query = select(User).filter(User.id == id)
            result = await self.async_session.execute(query)
            user = result.scalar_one_or_none()
            if user:
                return user

    async def get_users(self, page: int, per_page: int) -> UsersListResponse:

        total_count = await self.async_session.scalar(select(func.count()).select_from(User))

        offset = (page - 1) * per_page
        query = select(User).slice(offset, offset + per_page)


        users = await self.async_session.execute(query)
        user_list = [user_to_response(user) for user in users.scalars().all()]


        total_pages = ceil(total_count / per_page)

        return UsersListResponse(users=user_list, per_page=per_page, page=page, total=total_count,
                                 total_pages=total_pages)

    async def del_user(self, id: int) -> DeleteScheme:
        try:
            user = await self.get_user(id=id)
            if not user:
                return DeleteScheme(
                    message="User wasn't deleted",
                    id=-1
                )
            query = delete(User).where(User.id == id)
            result = await self.async_session.execute(query)
            await self.async_session.commit()
            if not result:
                return DeleteScheme(
                    message="User wasn't deleted",
                    id=-1
                )
            logger.info(f"User was deleted ID: {id}")
            return DeleteScheme(
                message="User was successfully deleted",
                id=id)

        except Exception as e:
            print(f"An error occurred while deleting user: {e}")

    async def update_user(self, id: int, request: UserScheme) -> User:
        try:
            user = await self.async_session.get(User, id)
            user = user.scalar_one_or_none()
            if user:
                user.username = request.username
                user.email = user.email
                user.password = hash_with_salt(password=request.password)
                user.city = request.city
                user.country = request.country
                user.phone = request.phone
                user.status = request.status
                user.roles = request.roles
                await self.async_session.commit()
                logger.info(f"User updated: ID {id}")
                return user
        except Exception as e:
            print(f"An error occurred while updating user: {e}")

    async def get_user_by_username(self, username: str) -> UserResponse:
        try:
            query = select(User).filter(User.username == username)
            result = await self.async_session.execute(query)
            user = result.scalar_one_or_none()
            if user:
                return user_to_response(user)
        except Exception as e:
            print(f"An error occurred while creating the user: {e}")
            raise e

    async def get_user_by_email(self, email: str) -> UserResponse:
        try:
            query = select(User).filter(User.email == email)
            result = await self.async_session.execute(query)
            user = result.scalar_one_or_none()
            if user:
                return user_to_response(user)

        except Exception as e:
            print(f"An error occurred while creating the user: {e}")
            raise e

    @staticmethod
    def create_password():
        password = str(datetime.datetime.utcnow())
        pass_hashed = hash_with_salt(password=password)
        return pass_hashed





