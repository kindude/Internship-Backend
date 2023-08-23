from __future__ import annotations

import datetime
import logging
from math import ceil

from dotenv import load_dotenv
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from models.Models import Company


from schemas.Company import CompanyScheme, CompanyResponse, CompanyListResponse
from schemas.Quiz import DeleteScheme

logger = logging.getLogger(__name__)
load_dotenv()


class CompanyRepository:

    def __init__(self, database: AsyncSession):
        self.async_session = database

    async def create_company(self, request: CompanyScheme) -> Company:
        try:
            company_dict = request.dict()
            company = Company(**company_dict)
            self.async_session.add(company)
            await self.async_session.commit()
            await self.async_session.refresh(company, attribute_names=["id"])
            logger.info(f"New user created: {request.name}")
            return company

        except Exception as e:
            print(f"An error occurred while creating the user: {e}")
            raise e

    async def get_company(self, id: int) -> CompanyResponse:
        query = select(Company).filter(Company.id == id)
        result = await self.async_session.execute(query)
        company = result.scalar_one_or_none()
        if company is not None:
            return company

    async def get_companies(self, page: int, per_page: int, current_user_id: int) -> CompanyListResponse:
        try:
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
            total_pages = ceil(total_count / per_page)
            return CompanyListResponse(companies=company_list, per_page=per_page, page=page, total=total_count,
                                       total_pages=total_pages)

        except Exception as e:
            print(f"An error occurred while deleting user: {e}")

    async def get_my_companies(self, page: int, per_page: int, current_user_id: int) -> CompanyListResponse:
        try:
            offset = (page - 1) * per_page

            query = select(Company).where(
                or_(
                    Company.owner_id == current_user_id
                )
            ).order_by(Company.id).offset(offset)

            companies = await self.async_session.execute(query)

            company_list = [self.company_to_response(company) for company in companies.scalars().all()]
            total_count = len(company_list)
            total_pages = ceil(total_count / per_page)
            return CompanyListResponse(companies=company_list, per_page=per_page, page=page, total=total_count,
                                       total_pages=total_pages)

        except Exception as e:
            print(f"An error occurred while deleting user: {e}")


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

    async def delete_company(self, id: int) -> DeleteScheme:
        try:
            company = await self.get_company(id=id)
            if not company:
                return DeleteScheme(
                    message="Company wasn't deleted",
                    id=-1
                )
            query = delete(Company).where(Company.id == id)
            result = await self.async_session.execute(query)
            await self.async_session.commit()
            if not result:
                return DeleteScheme(
                    message="Company wasn't deleted",
                    id=-1
                )
            logger.info(f"Company was deleted ID: {id}")
            return DeleteScheme(
                message="Company was successfully deleted",
                id=id)

        except Exception as e:
            print(f"An error occurred while deleting user: {e}")

    async def update_company(self, id: int, request: CompanyScheme) -> CompanyResponse:
        try:
            company = await self.async_session.get(Company, id)
            company = company.scalar_one_or_none()
            if company is not None:
                company.name = request.name
                company.description = request.description
                company.site = request.site
                company.city = request.city
                company.country = request.country
                company.owner_id = request.owner_id
                company.is_visible = request.is_visible
                await self.async_session.commit()
                logger.info(f"Company updated: ID {id}")
                return company
        except Exception as e:
            print(f"An error occurred while updating company: {e}")

    async def change_visibility(self, id: int, request: str) -> CompanyResponse:
        try:
            company = await self.async_session.get(Company, id)
            company = company.scalar_one_or_none()
            if company is not None:
                company.is_visible = request
                await self.async_session.commit()
                logger.info(f"Company's {id} visibility was updated to {request}")
                return company
        except Exception as e:
            print(f"An error occured while updating company: {e}")


