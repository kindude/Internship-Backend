from datetime import timedelta

from db.get_db import get_redis


class RedisRepository:
    def __init__(self):
        self.redis_client = None

    async def connect(self):
        self.redis_client = get_redis()


    async def disconnect(self):
        if self.redis_client:
            self.redis_client.close()

    async def save_quiz(self, quiz_data: dict):
        await self.connect()
        redis_key = f"quiz_result:{quiz_data['user_id']}:{quiz_data['quiz_id']}"
        self.redis_client.hmset(redis_key, quiz_data)
        expiration_time_seconds = int(timedelta(hours=48).total_seconds())
        self.redis_client.expire(redis_key, expiration_time_seconds)


    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.disconnect()

