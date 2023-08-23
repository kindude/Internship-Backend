import aioredis
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_session

from db.connect import connect_Postgres


async def get_db():
    async_session = await connect_Postgres()
    try:
        async with async_session as session:
            yield session
    finally:
        await async_session.close()


