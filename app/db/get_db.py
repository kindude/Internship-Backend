import aioredis
import redis

from db.connect import connect_Postgres


async def get_db():
    async_session = await connect_Postgres()
    try:
        async with async_session as session:
            yield session
    finally:
        await async_session.close()


async def get_redis():
    redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    try:
        yield redis_client
    finally:
        redis_client.close()


