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
from repositories.user_repository import action_to_resposne, user_to_response
from schemas.Action import ActionListResponse

from schemas.Company import CompanyScheme, CompanyResponse, CompanyDeleteScheme, CompanyListResponse, \
    CompanySchemeRequest
from schemas.User import UsersListResponse

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


    async def get_my_companies(self, page: int, per_page: int, current_user_id: int) -> CompanyListResponse:
        try:
            async with self.async_session as session:
                offset = (page - 1) * per_page

                query = select(Company).where(
                    or_(
                        Company.owner_id == current_user_id
                    )
                ).order_by(Company.id).offset(offset)

                companies = await session.execute(query)

                company_list = [self.company_to_response(company) for company in companies.scalars().all()]
                total_count = len(company_list)
                total_pages = ceil(total_count / per_page)
                return CompanyListResponse(companies=company_list, per_page=per_page, page=page, total=total_count,
                                           total_pages=total_pages)

        except Exception as e:
            print(f"An error occurred while deleting user: {e}")

