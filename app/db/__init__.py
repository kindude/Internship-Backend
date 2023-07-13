import asyncio
import redis
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker


# Postgre Connection
async def connect_to_postgre():
    database_url = 'postgresql+asyncpg://kindude:1234@localhost:5432/pg'
    engine = create_async_engine(database_url)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# Redis connection
async def connect_to_redis():
    r = redis.Redis()
    r.ping()
    return redis
