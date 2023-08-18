from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.connect import connect_Postgres


async def get_db():
    async_session = await connect_Postgres()
    try:
        yield async_session
    finally:
        await async_session.close()


