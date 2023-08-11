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
from schemas.Action import  ActionResponse, ActionListResponse
from schemas.User import UserResponse, UsersListResponse, UserScheme, UserDeleteScheme, UserLogin, Token, \
    UserResponseNoPass
from schemas.pasword_hashing import hash, hash_with_salt
from utils.create_token import create_token

logger = logging.getLogger(__name__)
load_dotenv()




class ActionRepository:

    def __init__(self, database: async_sessionmaker[AsyncSession]):
        self.async_session = database

    def create_invite(self, request_: ActionResponse) -> Action:
        invite = Action(**request_.dict())
        try:
            with self.async_session as session:
                session.add(invite)
                await session.commit()
                logger.info(f"New invite created")
                return invite
        except Exception as e:
            print(f"An error occurred while creating the invite: {e}")
            raise e

    def cancel_invite(self, request_: ActionResponse) -> Action:
        try:
            async with self.async_session as session:
                invite = await session.get(Action, request_.id)
                if invite is not None:
                    invite.status = "CANCELLED"
                    await session.commit()
                    logger.info(f"Invite status updated to 'CANCELLED'")
                    return invite
        except Exception as e:
            print(f"An error occured while updating an invite:{e}")

    async def accept_invite(self, request_: ActionResponse) -> Action:
        try:
            async with self.async_session as session:
                invite = await session.get(Action, request_.id)
                if invite is not None and invite.status == "PENDING":
                    invite.status = "ACCEPTED"
                    await session.commit()

                    user = await session.get(User, invite.user_id)
                    company = await session.get(Company, invite.company_id)
                    if user is not None and company is not None:
                        company.participants.append(user)
                        await session.commit()

                    logger.info(f"Invite accepted and user joined the company")
                    return invite
        except Exception as e:
            print(f"An error occurred while accepting an invite: {e}")
            raise e

    async def reject_invite(self, request_: ActionResponse) -> Action:
        try:
            async with self.async_session as session:
                invite = await session.get(Action, request_.id)
                if invite  and invite.status == "PENDING":
                    invite.status = "REJECTED"
                    await session.commit()
                    logger.info(f"Invite was declined by user")
                    return invite
        except Exception as e:
            print(f"An error occurred while rejecting an invite: {e}")
            raise e

    async def create_request(self, request_:ActionResponse) -> Action:
        try:
            async with self.async_session as session:
                request = Action(**request_.dict())
                session.add(request.dict())
                await session.commit()
                logger.info(f"New request created")
                return request
        except Exception as e:
            print(f"An error occured while creating a request:{e}")
            raise e

    async def cancel_request(self, request_:ActionResponse) -> Action:
        try:
            async with self.async_session as session:
                request = await session.get(Action, request_.id)
                if request and request.status == "PENDING":
                    request.status = "CANCELLED"
                    await session.commit()
                    logger.info(f"Request status was changed to CANCELLED by user")
                    return request

        except Exception as e:
            print(f"An error occured while cancelling the request: {e}")
            raise e

    async def accept_request(self, request_:ActionResponse) -> Action:
        try:
            with self.async_session as session:
                request = await session.get(Action, request_.id)
                if request and request.status == "PENDING":
                    request.status = "ACCEPTED"
                    await session.commit()

                    user = await session.get(User, request.user_id)
                    company = await session.get(Company, request.company_id)
                    if user is not None and company is not None:
                        company.participants.append(user)
                        await session.commit()

                    logger.info(f"Invite accepted and user joined the company")
                    return request

        except Exception as e:
            print(f"An error occured while accepting the request: {e}")
            raise e


    async def reject_request(self, request_:ActionResponse):
        try:
            with self.async_session as session:
                request = await session.get(Action, request_.id)
                if request and request.status == "PENDING":
                    request.status = "REJECTED"
                    await session.commit()

                    logger.info(f"Invite rejected")
                    return request
        except Exception as e:
            print(f"An error occured while rejecting the request")
            raise e

    
