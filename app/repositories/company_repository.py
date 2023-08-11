from __future__ import annotations

import datetime
import logging
from math import ceil

from dotenv import load_dotenv
from sqlalchemy import select, delete, desc
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_

from models.Models import Company, User, Action
from repositories.user_repository import action_to_resposne
from schemas.Action import ActionListResponse

from schemas.Company import CompanyScheme, CompanyResponse, CompanyDeleteScheme, CompanyListResponse, \
    CompanySchemeRequest

logger = logging.getLogger(__name__)
load_dotenv()


class CompanyRepository:

    def __init__(self, database: async_sessionmaker[AsyncSession]):
        self.async_session = database

    async def create_company(self, request: CompanyScheme) -> Company:
        try:
            company_dict = request.dict()
            company = Company(**company_dict)
            async with self.async_session as session:
                session.add(company)
                await session.commit()
                await session.refresh(company, attribute_names=["id"])
                logger.info(f"New user created: {request.name}")
                return company
        except Exception as e:
            print(f"An error occurred while creating the user: {e}")
            raise e

    async def get_company(self, id: int) -> CompanyResponse:
        async with self.async_session as session:
            query = select(Company).filter(Company.id == id)
            result = await session.execute(query)
            company = result.scalar_one_or_none()
            if company is None:
                return None
            return company

    async def get_companies(self, page: int, per_page: int, current_user_id: int) -> CompanyListResponse:

        offset = (page - 1) * per_page

        query = select(Company).where(
            or_(
                Company.is_visible == True,
                Company.owner_id == current_user_id
            )
        ).order_by(Company.id).offset(offset)

        companies = await self.async_session.execute(query)

        company_list = [self.company_to_response(company) for company in companies.scalars().all()]
        total_count = len(company_list)
        print(total_count)
        total_pages = ceil(total_count / per_page)

        return CompanyListResponse(companies=company_list, per_page=per_page, page=page, total=total_count,
                                   total_pages=total_pages)


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

    async def delete_company(self, id: int) -> CompanyDeleteScheme:
        try:
            company = await self.get_company(id=id)
            if company:
                async with self.async_session as session:
                    query = delete(Company).where(Company.id == id)
                    result = await session.execute(query)
                    await session.commit()
                    if result:
                        logger.info(f"Company was deleted ID: {id}")
                        return CompanyDeleteScheme(
                            message="Company was successfully deleted",
                            id=id
                        )
                    else:
                        return CompanyDeleteScheme(
                            message="Company wasn't deleted",
                            id=-1
                        )
            else:
                return CompanyDeleteScheme(
                    message="Company wasn't deleted",
                    id=-1
                )

        except Exception as e:
            print(f"An error occurred while deleting user: {e}")

    async def update_company(self, id: int, request: CompanyScheme) -> CompanyResponse:
        try:
            async with self.async_session as session:
                company = await session.get(Company, id)
                if company is not None:
                    company.name = request.name
                    company.description = request.description
                    company.site = request.site
                    company.city = request.city
                    company.country = request.country
                    company.owner_id = request.owner_id
                    company.is_visible = request.is_visible
                    await session.commit()
                    logger.info(f"Company updated: ID {id}")
                    return company
        except Exception as e:
            print(f"An error occurred while updating company: {e}")

    async def change_visibility(self, id: int, request: str) -> CompanyResponse:
        try:
            async with self.async_session as session:
                company = await session.get(Company, id)
                if company is not None:
                    company.is_visible = request
                    await session.commit()
                    logger.info(f"Company's {id} visibility was updated to {request}")
                    return company
        except Exception as e:
            print(f"An error occured while updating company: {e}")

    async def remove_user_from_company(self, user_id: int, company_id: int) -> bool:
        try:
            async with self.async_session as session:
                company = await session.get(Company, company_id)
                user = await session.get(User, user_id)

                if company is not None and user is not None:
                    if user in company.participants:
                        company.participants.remove(user)
                        await session.commit()
                        logger.info(f"User {user.username} removed from company {company.name}")
                        return True
                    else:
                        logger.warning(f"User {user.username} is not a member of company {company.name}")
                        return False
                else:
                    logger.warning("Company or user not found")
                    return False
        except Exception as e:
            print(f"An error occurred while removing user from company: {e}")
            raise e

    async def get_all_invites(self, company_id:int) -> ActionListResponse:
        try:
            with self.async_session as session:
                query = select(Action).filter(Action.company_id == company_id and Action.type == "INVITE")
                invites = await session.execute(query)
                if invites is  None:
                    return None

                else:
                    invites_list = [action_to_resposne(invite) for invite in invites.scalars.all()]
                    return ActionListResponse(actions=invites_list)
        except Exception as e:
            print(f"An error occurred while getting invites: {e}")
            raise e

    async def get_all_requests(self, company_id:int) -> ActionListResponse:
        try:
            with self.async_session as session:
                query = select(Action).filter(Action.company_id == company_id and Action.type == "REQUEST")
                requests = await session.execute(query)
                if requests is None:
                    return None

                else:
                    requests_list = [action_to_resposne(request) for request in requests.scalars.all()]
                    return ActionListResponse(actions=requests_list)
        except Exception as e:
            print(f"An error occurred while getting invites: {e}")
            raise e

