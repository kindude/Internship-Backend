from __future__ import annotations

import datetime
import logging
from math import ceil

from dotenv import load_dotenv
from sqlalchemy import select, delete, desc
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from models.Models import User, Invitation
from schemas.Invitation import InvitationResponse, InvitationReponseList
from schemas.User import UserResponse, UsersListResponse, UserScheme, UserDeleteScheme, UserLogin, Token, \
    UserResponseNoPass
from schemas.pasword_hashing import hash, hash_with_salt
from utils.create_token import create_token

logger = logging.getLogger(__name__)
load_dotenv()


class UserRepository:

    def __init__(self, database: async_sessionmaker[AsyncSession]):
        self.async_session = database

    async def authenticate_user(self, request: UserLogin) -> Token:
        try:
            user = await self.get_user_by_email(email=request.email)
            hashed_request_password = hash_with_salt(request.password)
            print(hashed_request_password)
            print(user.password)
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
            async with self.async_session as session:
                session.add(user)
                await session.commit()
                logger.info(f"New user created: {request.username}")
                return user
        except Exception as e:
            print(f"An error occurred while creating the user: {e}")
            raise e

    async def get_user(self, id: int) -> UserResponseNoPass:
        async with self.async_session as session:
            query = select(User).filter(User.id == id)
            result = await session.execute(query)
            user = result.scalar_one_or_none()
            if user is None:
                return None
            return user

    async def get_users(self, page: int, per_page: int) -> UsersListResponse:

        total_count = await self.async_session.scalar(select(func.count()).select_from(User))

        offset = (page - 1) * per_page
        query = select(User).slice(offset, offset + per_page)


        users = await self.async_session.execute(query)
        user_list = [self.user_to_response(user) for user in users.scalars().all()]


        total_pages = ceil(total_count / per_page)

        return UsersListResponse(users=user_list, per_page=per_page, page=page, total=total_count,
                                 total_pages=total_pages)

    def user_to_response(self, user: User) -> UserResponse:
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

    async def update_user(self, id: int, request: UserScheme) -> User:
        try:
            async with self.async_session as session:
                user = await session.get(User, id)
                if user is not None:
                    user.username = request.username
                    user.email = user.email
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

    async def get_user_by_username(self, username: str) -> UserResponse:
        try:
            async with self.async_session as session:
                query = select(User).filter(User.username == username)
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
        except Exception as e:
            print(f"An error occurred while creating the user: {e}")
            raise e

    def create_password(self):
        password = str(datetime.datetime.utcnow())
        pass_hashed = hash_with_salt(password=password)
        return pass_hashed

    async def get_all_invitations(self, id: int) -> InvitationReponseList:
        try:
            async with self.async_session as session:
                query = select(Invitation).filter(Invitation.user_id == id)
                invitations = session.execute(query)
                if invitations is None:
                    return None
                else:
                    invitations_list = [self.invititaion_to_resposne(invite) for invite in invitations.scalars.all()]
                    return invitations_list
        except Exception as e:
            print(f"An error occurred while creating the user: {e}")
            raise e


    def invititaion_to_resposne(self, invite:Invitation) -> InvitationResponse:
        return InvitationResponse(
            id = invite.id,
            user_id = invite.user_id,
            company_id = invite.company_id,
            status= invite.status
        )


