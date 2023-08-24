import uuid
from datetime import timedelta


from db.get_db import get_redis


class RedisRepository:
    def __init__(self):
        self.redis_client = None

    async def connect(self):
        self.redis_client = await get_redis()

    async def disconnect(self):
        if self.redis_client:
            self.redis_client.close()

    async def save_quiz(self, quiz_data: dict):
        await self.connect()
        redis_key = f"quiz_result:{quiz_data['company_id']}:{quiz_data['user_id']}:{quiz_data['quiz_id']}:{uuid.uuid4()}"
        self.redis_client.hmset(redis_key, quiz_data)
        expiration_time_seconds = int(timedelta(hours=48).total_seconds())
        self.redis_client.expire(redis_key, expiration_time_seconds)

    async def get_user_results_from_database(self, company_id, user_id):
        await self.connect()
        redis_key_pattern = f"quiz_result:{company_id}:{user_id}:*"

        matching_keys = self.redis_client.keys(redis_key_pattern)

        user_results = []

        for redis_key in matching_keys:
            quiz_data = self.redis_client.hgetall(redis_key)
            user_results.append(quiz_data)

        return user_results

    async def get_company_results(self, company_id):
        await self.connect()
        redis_key_pattern = f"quiz_result:{company_id}:*"

        matching_keys = self.redis_client.keys(redis_key_pattern)

        company_results = []

        for redis_key in matching_keys:
            quiz_data = self.redis_client.hgetall(redis_key)
            company_results.append(quiz_data)

        return company_results


    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.disconnect()

