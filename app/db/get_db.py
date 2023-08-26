import aioredis
import redis

from ENV import REDIS_PORT, REDIS_HOST

from db.connect import connect_Postgres


async def get_db():
    async_session = await connect_Postgres()
    try:
        async with async_session as session:
            yield session
    finally:
        await async_session.close()


async def get_redis():
    return redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)



