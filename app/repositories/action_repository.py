from __future__ import annotations


import logging
from math import ceil

from dotenv import load_dotenv
from sqlalchemy import select, func, and_
from sqlalchemy.sql import update
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.Models import User, Action, Company, Question
from repositories.user_repository import action_to_resposne, user_to_response, action_to_scheme
from schemas.Action import ActionResponse, ActionListResponse, ActionScheme
from schemas.Company import CompanyListResponse, CompanyResponse
from schemas.User import UsersListResponse, UserResponseNoPass

logger = logging.getLogger(__name__)
load_dotenv()




class ActionRepository:

    def __init__(self, database: AsyncSession):
        self.async_session = database

    async def create_invite(self, request_: ActionResponse) -> Action:
        invite = Action(**request_.dict())
        try:
            self.async_session.add(invite)
            await self.async_session.commit()
            logger.info(f"New invite created")
            return invite
        except Exception as e:
            print(f"An error occurred while creating the invite: {e}")
            raise e

    async def cancel_invite(self, request_: ActionResponse) -> Action:
        try:
            invite = await self.async_session.get(Action, request_.id)
            invite = invite.scalar_one_or_none()
            if invite is not None:
                invite.status = "CANCELLED"
                await self.async_session.commit()
                logger.info(f"Invite status updated to 'CANCELLED'")
                return invite
        except Exception as e:
            print(f"An error occured while updating an invite:{e}")

    async def accept_invite(self, request_: ActionScheme) -> Action:
        try:
            invite = await self.async_session.get(Action, request_.id)
            invite = invite.scalar_one_or_none()
            if invite is not None and invite.status == "PENDING":
                invite.status = "ACCEPTED"
                invite.type_of_action = "MEMBER"
                await self.async_session.commit()
                logger.info(f"Invite accepted and user joined the company")
                return invite
        except Exception as e:
            print(f"An error occurred while accepting an invite: {e}")
            raise e

    async def reject_invite(self, request_: ActionScheme) -> Action:
        try:
            invite = await self.async_session.get(Action, request_.id)
            invite = invite.scalar_one_or_none()
            if invite and invite.status == "PENDING":
                invite.status = "REJECTED"
                await self.async_session.commit()
                logger.info(f"Invite was declined by user")
                return invite
        except Exception as e:
            print(f"An error occurred while rejecting an invite: {e}")
            raise e

    async def create_request(self, request_: ActionResponse) -> Action:
        try:
            request = Action(**request_.dict())
            self.async_session.add(request)
            await self.async_session.commit()
            logger.info(f"New request created")
            return request
        except Exception as e:
            print(f"An error occured while creating a request:{e}")
            raise e

    async def cancel_request(self, request_: ActionScheme) -> Action:
        try:
            request = await self.async_session.get(Action, request_.id)
            request = request.scalar_one_or_none()
            if request and request.status == "PENDING":
                request.status = "CANCELLED"
                await self.async_session.commit()
                logger.info(f"Request status was changed to CANCELLED by user")
                return request
        except Exception as e:
            print(f"An error occured while cancelling the request: {e}")
            raise e

    async def accept_request(self, request_: ActionScheme) -> Action:
        try:
            request = await self.async_session.get(Action, request_.id)
            request = request.scalar_one_or_none()
            if request and request.status == "PENDING":
                request.status = "ACCEPTED"
                request.type_of_action = "MEMBER"
                await self.async_session.commit()
                logger.info(f"Invite accepted and user joined the company")
                return request

        except Exception as e:
            print(f"An error occured while accepting the request: {e}")
            raise e

    async def reject_request(self, request_:ActionResponse):
        try:
            request = await self.async_session.get(Action, request_.id)
            request = request.scalar_one_or_none()
            request.status = "REJECTED"
            await self.async_session.commit()
            logger.info(f"Invite rejected")
            return request
        except Exception as e:
            print(f"An error occured while rejecting the request")
            raise e

    async def leave_company(self, user_id: int, company_id:int) -> bool:
        try:
            query = select(Action).options(selectinload(Action.user)).filter(and_(
                Action.user_id == user_id,
                Action.company_id == company_id,
                Action.type_of_action == "MEMBER"
            ))

            actions = await self.async_session.execute(query)
            actions = actions.scalars().all()
            if actions:
                for action in actions:
                    await self.async_session.delete(action)
                await self.async_session.commit()
                logger.info(f"User with ID {user_id} left the company")
                return True
            else:
                logger.warning(f"User with ID {user_id} is not a member of any company")
                return False

        except Exception as e:
            print(f"An error occurred while leaving company: {e}")
            raise e

    async def get_all_invites_user(self, user_id: int) -> ActionListResponse:
        try:
            query = select(Action).filter(and_(Action.user_id == user_id, Action.type_of_action == "INVITE"))
            invites = await self.async_session.execute(query)
            if invites is None:
                invites_list = [action_to_scheme(invite) for invite in invites.scalars().all()]
                return ActionListResponse(actions=invites_list)
        except Exception as e:
            print(f"An error occurred while getting invites: {e}")
            raise e

    def company_to_response(self, company: Company) -> CompanyResponse:
        return CompanyResponse(
            id=company.id,
            name=company.name,
            description=company.description,
            site=company.site,
            city=company.city,
            country=company.country,
            is_visible=company.is_visible,
            owner_id=company.owner_id,
        )

    async def get_all_companies_im_in(self, page: int, per_page: int, current_user_id: int) -> CompanyListResponse:
        offset = (page - 1) * per_page
        try:
            query = select(Company).join(Action).filter(and_(Action.type_of_action == "MEMBER", Action.user_id == current_user_id)).order_by(Company.id).offset(offset)
            companies = await self.async_session.execute(query)
            if companies is None:
                company_list = [self.company_to_response(company) for company in companies.scalars().all()]
                total_count = len(company_list)
                total_pages = ceil(total_count / per_page)
                return CompanyListResponse(companies=company_list, per_page=per_page, page=page, total=total_count,
                                           total_pages=total_pages)
        except Exception as e:
            print(f"An error occurred while getting invites: {e}")
            raise e

    async def get_all_requests_user(self, user_id: int) -> ActionListResponse:
        try:
            query = select(Action).filter(and_(Action.user_id == user_id, Action.type_of_action == "REQUEST"))
            requests = await self.async_session.execute(query)
            print(requests)
            if requests is None:
                requests_list = [action_to_scheme(request) for request in requests.scalars().all()]
                return ActionListResponse(actions=requests_list)
        except Exception as e:
            print(f"An error occurred while creating the user: {e}")
            raise e

    async def remove_user_from_company(self, user_id: int, company_id: int) -> bool:
        try:
            query = select(Action).filter(and_(
                Action.user_id == user_id,
                Action.company_id == company_id,
                Action.type_of_action == "MEMBER"
            ))
            action = await self.async_session.execute(query)
            action = action.scalar_one_or_none()
            if action:
                await self.async_session.delete(action)
                await self.async_session.commit()
                logger.info(f"User with ID {user_id} removed from company with ID {company_id}")
                return True
            else:
                logger.warning(f"User with ID {user_id} is not a member of company with ID {company_id}")
                return False

        except Exception as e:
            print(f"An error occurred while removing user from company: {e}")
            raise e

    async def get_all_invites_company(self, company_id:int) -> ActionListResponse:
        try:
            query = select(Action).filter(and_(Action.company_id == company_id, Action.type_of_action == "INVITE"))
            invites = await self.async_session.execute(query)
            if invites is not None:
                invites_list = [action_to_scheme(invite) for invite in invites.scalars().all()]
                return ActionListResponse(actions=invites_list)
        except Exception as e:
            print(f"An error occurred while getting invites: {e}")
            raise e

    async def get_all_requests_company(self, company_id: int) -> ActionListResponse:
        try:
            query = select(Action).filter(and_(Action.company_id == company_id, Action.type_of_action == "REQUEST"))
            requests = await self.async_session.execute(query)
            if requests is not None:
                requests_list = [action_to_scheme(request) for request in requests.scalars().all()]
                return ActionListResponse(actions=requests_list)
        except Exception as e:
            print(f"An error occurred while getting invites: {e}")
            raise e

    async def get_users_in_company(self, company_id: int, per_page: int, page: int) -> UsersListResponse:
        try:
            stmt = select(func.count(User.id)).join(Action).filter(
                (Action.type_of_action == "MEMBER") & (Action.user_id == User.id) & (Action.company_id == company_id)
            )
            total_users_result = await self.async_session.execute(stmt)
            total_users = total_users_result.scalar()

            total_pages = (total_users + per_page - 1) // per_page

            stmt = select(User).join(Action).where(
                (Action.type_of_action == "MEMBER") & (Action.user_id == User.id) & (Action.company_id == company_id)
            ).offset((page - 1) * per_page).limit(per_page)

            user_list = await self.async_session.execute(stmt)

            user_list_response = [user_to_response(user) for user in user_list.scalars().all()]

            return UsersListResponse(users=user_list_response, per_page=per_page, page=page, total=total_users,
                                     total_pages=total_pages)

        except Exception as e:
            print(f"An error occurred while getting users in company: {e}")
            raise e

    async def if_member(self, user_id: int, company_id: int) -> bool:
        try:
            query = select(User).join(Action).where(
                (Action.type_of_action == "MEMBER") & (Action.user_id == user_id) & (Action.company_id == company_id)
            )
            user = await self.async_session.execute(query)
            user = user.scalar_one_or_none()
            return user
        except Exception as e:
            print(f"An error occurred while getting users in company: {e}")
            raise e


    async def add_admin(self, user_id:int, company_id:int) -> UserResponseNoPass:
        try:
            user = await self.async_session.get(User, user_id)
            user = user.scalar_one_or_none()
            if await self.if_member(user_id, company_id):
                if user:
                    if "ADMIN" not in user.roles:
                        user.roles.append("ADMIN")
                        updated_roles = user.roles.copy()
                        stmt = update(User).where(User.id == user_id).values(roles=updated_roles)
                        await self.async_session.execute(stmt)
                        await self.async_session.commit()
                        return user
        except Exception as e:
            print(f"An error occurred while getting users in company: {e}")
            raise e

    async def remove_admin(self, id: int) -> UserResponseNoPass:
        try:
            user = await self.async_session.get(User, id)
            user = user.scalar_one_or_none()
            if user:
                if "ADMIN" in user.roles:
                    user.roles.remove("ADMIN")
                    updated_roles = user.roles.copy()
                    stmt = update(User).where(User.id == id).values(roles=updated_roles)
                    await self.async_session.execute(stmt)
                    await self.async_session.commit()
                    return user
        except Exception as e:
            print(f"An error occurred while removing admin role: {e}")
            raise e

    async def get_all_admins(self, company_id: int, per_page: int, page: int) -> UsersListResponse:
        try:
            stmt = (
                select(User)
                .join(Action)
                .where((Action.company_id == company_id) & (User.roles.op('@>')(["ADMIN"])))
                .distinct()
            )

            result = await self.async_session.execute(stmt)
            user_list = result.scalars().all()

            total_users = len(user_list)
            total_pages = ceil(total_users / per_page)

            start_index = (page - 1) * per_page
            end_index = start_index + per_page
            users_on_page = user_list[start_index:end_index]

            user_list_response = [user_to_response(user) for user in users_on_page]
            return UsersListResponse(
                users=user_list_response,
                per_page=per_page,
                page=page,
                total=total_users,
                total_pages=total_pages
            )
        except Exception as e:
            print(f"An error occurred while getting all admins: {e}")
            raise e

    async def cancel_request_company(self, request_: ActionScheme) -> Action:
        try:
            request = await self.async_session.get(Action, request_.id)
            request = request.scalar_one_or_none()
            if request and request.status == "PENDING":
                request.status = "CANCELLED"
                await self.async_session.commit()
                logger.info(f"Request status was changed to CANCELLED by user")
                return request

        except Exception as e:
            print(f"An error occured while cancelling the request: {e}")
            raise e


