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


redis_pool = None

async def init_redis():
    global redis_pool
    redis_pool = await aioredis.create_redis_pool("redis://localhost", encoding="utf-8")

async def close_redis():
    global redis_pool
    if redis_pool:
        redis_pool.close()
        await redis_pool.wait_closed()