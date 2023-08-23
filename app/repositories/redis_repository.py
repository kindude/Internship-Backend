from datetime import timedelta

import redis

from db.connect import connect_Redis


class RedisRepository:
    def __init__(self):
        self.redis_client = None

    async def connect(self):
        self.redis_client = redis.Redis(host='redis', port=6379, decode_responses=True)
        print(f"redis connected")

    async def disconnect(self):
        if self.redis_client:
            self.redis_client.close()

    async def save_quiz(self, quiz_data: dict):
        await self.connect()
        print(quiz_data['user_id'])
        redis_key = f"quiz_result:{quiz_data['user_id']}:{quiz_data['quiz_id']}:{quiz_data['time']}"
        self.redis_client.hmset(redis_key, quiz_data)
        expiration_time_seconds = int(timedelta(hours=48).total_seconds())
        self.redis_client.expire(redis_key, expiration_time_seconds)


    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.disconnect()

