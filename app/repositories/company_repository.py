from __future__ import annotations

import datetime
import logging

from dotenv import load_dotenv
from sqlalchemy import select, delete, desc
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select

from models.Company import Company
from models.User import User
from schemas.Company import CompanyScheme, CompanyResponse
from schemas.User import UserResponse, UsersListResponse, UserScheme, UserDeleteScheme, UserLogin, Token
from schemas.pasword_hashing import hash, hash_with_salt
from utils.create_token import create_token

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
                logger.info(f"New user created: {request.name}")
                return company
        except Exception as e:
            print(f"An error occurred while creating the user: {e}")
            raise e

    async def get_user(self, id: int) -> CompanyResponse:
        async with self.async_session as session:
            query = select(Company).filter(Company.id == id)
            result = await session.execute(query)
            company = result.scalar_one_or_none()
            if company is None:
                return None
            return company

    async def get_users(self, page: int = 1, per_page: int = 10) -> UsersListResponse:
        offset = (page - 1) * per_page
        query = select(Company).slice(offset, offset + per_page)
        companies = await self.async_session.execute(query)
        company_list = [self.user_to_scheme(company) for company in companies.scalars().all()]
        return UsersListResponse(users=company_list)

    def user_to_scheme(self, company: Company) -> CompanyResponse:
        return CompanyResponse(
            id=company.id,
            name=company.name,
            description=company.description,
            site=company.site,
            city=company.city,
            country=company.country,
            owner_id=company.owner_id,
        )

    # async def del_user(self, id: int) -> UserDeleteScheme:
    #     try:
    #         user = await self.get_user(id=id)
    #         if user:
    #             async with self.async_session as session:
    #                 query = delete(User).where(User.id == id)
    #                 result = await session.execute(query)
    #                 await session.commit()
    #                 if result:
    #                     logger.info(f"Пользователь удален: ID {id}")
    #                     return UserDeleteScheme(
    #                         message="User was successfully deleted",
    #                         id=id
    #                     )
    #                 else:
    #                     return UserDeleteScheme(
    #                         message="User wasn't deleted",
    #                         id=-1
    #                     )
    #         else:
    #             return UserDeleteScheme(
    #                 message="User wasn't deleted",
    #                 id=-1
    #             )
    #
    #     except Exception as e:
    #         print(f"An error occurred while deleting user: {e}")
    #
    # async def update_user(self, id: int, request: UserScheme) -> UserResponse:
    #     try:
    #         async with self.async_session as session:
    #             user = await session.get(User, id)
    #             if user is not None:
    #                 user.username = request.username
    #                 user.email = user.email
    #                 user.password = hash(password=request.password)
    #                 user.city = request.city
    #                 user.country = request.country
    #                 user.phone = request.phone
    #                 user.status = request.status
    #                 user.roles = request.roles
    #                 await session.commit()
    #                 logger.info(f"User updated: ID {id}")
    #                 return user
    #     except Exception as e:
    #         print(f"An error occurred while updating user: {e}")

