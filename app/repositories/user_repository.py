import hashlib
import math
import os
import logging
from sqlalchemy.orm import Session
from app.db import AsyncSession
from app.models.User import User
from dotenv import load_dotenv


# Создание объекта логгера
logger = logging.getLogger(__name__)
load_dotenv()
class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(self, username, email, password, city, country, phone, status, roles):
        try:
            salt = os.getenv("SALT")
            database_password = password + salt
            hashed = hashlib.md5(database_password.encode()).hexdigest()
            user = User(username, email, hashed, city, country, phone, status, roles)
            self.session.add(user)
            await self.session.commit()
            logger.info(f"Создан новый пользователь: {username}")

        except Exception as e:
            # Handle the specific exception here
            print(f"An error occurred during user creation: {e}")

    async def get_user(self, user_id: int) -> User:
        try:
            return await self.session.query(User).filter(User.id == user_id).first()
        except Exception as e:
            # Handle the specific exception here
            print(f"An error occurred while retrieving user: {e}")
            return None

    async def get_users(self, page: int = 1, per_page: int = 10):
        query = self.session.query(User)
        total_count = query.count()

        # Calculate the total number of pages
        total_pages = math.ceil(total_count / per_page)

        # Adjust the page number if it exceeds the total pages
        page = min(page, total_pages)

        # Calculate the offset and limit based on the page and per_page values
        offset = (page - 1) * per_page
        limit = per_page

        # Apply pagination to the query
        query = query.offset(offset).limit(limit)

        # Execute the query and retrieve the users
        users = await query.all()

        return {
            'users': users,
            'page': page,
            'per_page': per_page,
            'total_pages': total_pages,
            'total_count': total_count
        }

    async def del_user(self, user_id: int):
        try:
            user = await self.get_user(user_id)
            if user:
                await self.session.delete(user)
                await self.session.commit()
            logger.info(f"Пользователь удален: ID {user_id}")
        except Exception as e:
            print(f"An error occurred while deleting user: {e}")

    async def update_user(self, user_id: int, username: str, email: str, password: str, city: str, country: str,
                          phone: str, status: bool, roles: list):
        try:
            user = await self.get_user(user_id)
            if user:
                user.username = username
                user.email = email
                user.password = password
                user.city = city
                user.country = country
                user.phone = phone
                user.status = status
                user.roles = roles
                await self.session.commit()
                logger.info(f"Пользователь обновлен: ID {user_id}")
        except Exception as e:
            print(f"An error occurred while updating user: {e}")

